#property strict
#property version   "1.00"
#property description "FMP Phase 8B read-only multi-symbol demo quote bridge"

const string BRIDGE_PROTOCOL = "fmp-mt5-demo-multisymbol-file-bridge-v1";
const string SERVER_DEMO_1 = "FPMarketsSC-Demo";
const string SERVER_DEMO_2 = "FPMarketsSC-Demo2";
const int HEARTBEAT_SECONDS = 5;
const int MAX_CLOCK_SKEW_SECONDS = 5;

int g_file = INVALID_HANDLE;
string g_bridge_file = "";
string g_bridge_session_id = "";
string g_server = "";
string g_account_fingerprint = "";
long g_last_tick_time_msc = 0;

bool AllowedServer(const string server)
  {
   return server == SERVER_DEMO_1 || server == SERVER_DEMO_2;
  }

bool BridgeFileForSymbol(const string symbol, string &path)
  {
   if(symbol == "EURUSD")
     {
      path = "FMP\\phase8b-eurusd-feed.jsonl";
      return true;
     }
   if(symbol == "GBPUSD")
     {
      path = "FMP\\phase8b-gbpusd-feed.jsonl";
      return true;
     }
   if(symbol == "USDJPY")
     {
      path = "FMP\\phase8b-usdjpy-feed.jsonl";
      return true;
     }
   return false;
  }

string BytesToHex(const uchar &bytes[])
  {
   string value = "";
   const int count = ArraySize(bytes);
   for(int i = 0; i < count; ++i)
      value += StringFormat("%02x", (uint)bytes[i]);
   return value;
  }

string Sha256Text(const string value)
  {
   uchar data[];
   uchar key[];
   uchar digest[];
   const int chars = StringLen(value);
   if(StringToCharArray(value, data, 0, chars, CP_UTF8) != chars)
      return "";
   if(CryptEncode(CRYPT_HASH_SHA256, data, key, digest) != 32)
      return "";
   return BytesToHex(digest);
  }

long BridgeAuditTimeMsc()
  {
   return ((long)TimeGMT()) * 1000;
  }

string MakeBridgeSessionId(
   const long login,
   const string server,
   const string symbol
)
  {
   const string seed = StringFormat(
      "%I64d|%s|%s|%I64d|%I64u",
      login,
      server,
      symbol,
      (long)TimeGMT(),
      GetMicrosecondCount()
   );
   return Sha256Text(seed);
  }

bool WriteRecord(const string line)
  {
   if(g_file == INVALID_HANDLE)
      return false;
   if(FileWriteString(g_file, line + "\n") <= 0)
      return false;
   FileFlush(g_file);
   return true;
  }

string CommonFields(const string record_type)
  {
   return StringFormat(
      "{\"record_type\":\"%s\",\"protocol\":\"%s\",\"bridge_session_id\":\"%s\",\"symbol\":\"%s\",\"server\":\"%s\",\"account_fingerprint\":\"%s\"",
      record_type,
      BRIDGE_PROTOCOL,
      g_bridge_session_id,
      _Symbol,
      g_server,
      g_account_fingerprint
   );
  }

bool EmitBridgeStart()
  {
   const long bridge_start_time_msc = BridgeAuditTimeMsc();
   if(bridge_start_time_msc <= 0)
      return false;
   const string line = StringFormat(
      "%s,\"account_mode\":\"DEMO\",\"bridge_start_time_msc\":%I64d}",
      CommonFields("BRIDGE_START"),
      bridge_start_time_msc
   );
   return WriteRecord(line);
  }

bool TickUtcTimeMsc(const MqlTick &tick, long &utc_time_msc)
  {
   const long server_seconds = (long)TimeCurrent();
   const long utc_seconds = (long)TimeGMT();
   const long raw_offset_seconds = server_seconds - utc_seconds;
   const long rounded_offset_seconds =
      ((long)MathRound((double)raw_offset_seconds / 3600.0)) * 3600;

   if(MathAbs((double)(raw_offset_seconds - rounded_offset_seconds)) > MAX_CLOCK_SKEW_SECONDS)
      return false;

   utc_time_msc = tick.time_msc - rounded_offset_seconds * 1000;
   return utc_time_msc > 0;
  }

bool EmitTick(const MqlTick &tick, const long source_time_msc)
  {
   const string line = StringFormat(
      "%s,\"source_time_msc\":%I64d,\"bid\":%s,\"ask\":%s,\"flags\":%u}",
      CommonFields("TICK"),
      source_time_msc,
      DoubleToString(tick.bid, _Digits),
      DoubleToString(tick.ask, _Digits),
      (uint)tick.flags
   );
   return WriteRecord(line);
  }

bool EmitHeartbeat()
  {
   const long bridge_emitted_time_msc = BridgeAuditTimeMsc();
   if(bridge_emitted_time_msc <= 0)
      return false;
   const string last_tick_json =
      g_last_tick_time_msc > 0
      ? StringFormat("%I64d", g_last_tick_time_msc)
      : "null";
   const string line = StringFormat(
      "%s,\"bridge_emitted_time_msc\":%I64d,\"last_tick_time_msc\":%s}",
      CommonFields("BRIDGE_HEARTBEAT"),
      bridge_emitted_time_msc,
      last_tick_json
   );
   return WriteRecord(line);
  }

int OnInit()
  {
   const ENUM_ACCOUNT_TRADE_MODE mode =
      (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   if(mode != ACCOUNT_TRADE_MODE_DEMO)
     {
      Print("FMP Phase 8B bridge refused: demo account required");
      return INIT_FAILED;
     }

   if(!BridgeFileForSymbol(_Symbol, g_bridge_file))
     {
      Print("FMP Phase 8B bridge refused: unsupported chart symbol");
      return INIT_FAILED;
     }

   g_server = AccountInfoString(ACCOUNT_SERVER);
   if(!AllowedServer(g_server))
     {
      Print("FMP Phase 8B bridge refused: unapproved demo server");
      return INIT_FAILED;
     }

   const long login = AccountInfoInteger(ACCOUNT_LOGIN);
   g_account_fingerprint = Sha256Text(StringFormat("%I64d", login));
   g_bridge_session_id = MakeBridgeSessionId(login, g_server, _Symbol);
   if(
      StringLen(g_account_fingerprint) != 64
      || StringLen(g_bridge_session_id) != 64
   )
     {
      Print("FMP Phase 8B bridge refused: identity hashing failed");
      return INIT_FAILED;
     }

   FileDelete(g_bridge_file, FILE_COMMON);
   g_file = FileOpen(
      g_bridge_file,
      FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE,
      0,
      CP_UTF8
   );
   if(g_file == INVALID_HANDLE)
     {
      Print("FMP Phase 8B bridge refused: transport file unavailable");
      return INIT_FAILED;
     }

   if(!EmitBridgeStart())
     {
      FileClose(g_file);
      g_file = INVALID_HANDLE;
      Print("FMP Phase 8B bridge refused: startup record write failed");
      return INIT_FAILED;
     }

   if(!EventSetTimer(HEARTBEAT_SECONDS))
     {
      FileClose(g_file);
      g_file = INVALID_HANDLE;
      Print("FMP Phase 8B bridge refused: heartbeat timer unavailable");
      return INIT_FAILED;
     }

   return INIT_SUCCEEDED;
  }

void OnTick()
  {
   if(g_file == INVALID_HANDLE)
      return;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return;
   if(tick.time_msc <= 0)
      return;
   if(!MathIsValidNumber(tick.bid) || !MathIsValidNumber(tick.ask))
      return;
   if(tick.bid <= 0.0 || tick.ask <= 0.0 || tick.ask < tick.bid)
      return;

   long source_time_msc = 0;
   if(!TickUtcTimeMsc(tick, source_time_msc))
      return;

   if(EmitTick(tick, source_time_msc))
      g_last_tick_time_msc = source_time_msc;
  }

void OnTimer()
  {
   if(g_file == INVALID_HANDLE)
      return;
   EmitHeartbeat();
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   if(g_file != INVALID_HANDLE)
     {
      FileFlush(g_file);
      FileClose(g_file);
      g_file = INVALID_HANDLE;
     }
  }
