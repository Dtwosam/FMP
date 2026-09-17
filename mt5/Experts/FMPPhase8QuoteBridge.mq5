#property strict
#property version   "1.00"
#property description "FMP Phase 8 read-only USDJPY demo quote bridge"

const string BRIDGE_PROTOCOL = "fmp-mt5-demo-file-bridge-v1";
const string BRIDGE_FILE = "FMP\\phase8-usdjpy-feed.jsonl";
const string BRIDGE_SYMBOL = "USDJPY";
const string SERVER_DEMO_1 = "FPMarketsSC-Demo";
const string SERVER_DEMO_2 = "FPMarketsSC-Demo2";
const int HEARTBEAT_SECONDS = 5;

int g_file = INVALID_HANDLE;
string g_session_id = "";
string g_server = "";
string g_account_fingerprint = "";
long g_last_tick_time_msc = 0;

bool AllowedServer(const string server)
  {
   return server == SERVER_DEMO_1 || server == SERVER_DEMO_2;
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

string MakeSessionId(const long login, const string server)
  {
   const string seed = StringFormat("%I64d|%s|%I64d|%I64u", login, server, (long)TimeLocal(), GetMicrosecondCount());
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
      "{\"record_type\":\"%s\",\"protocol\":\"%s\",\"session_id\":\"%s\",\"symbol\":\"%s\",\"server\":\"%s\",\"account_fingerprint\":\"%s\"",
      record_type,
      BRIDGE_PROTOCOL,
      g_session_id,
      BRIDGE_SYMBOL,
      g_server,
      g_account_fingerprint
   );
  }

bool EmitBridgeStart()
  {
   return WriteRecord(CommonFields("BRIDGE_START") + "}");
  }

bool EmitTick(const MqlTick &tick)
  {
   const string line = StringFormat(
      "%s,\"source_time_msc\":%I64d,\"bid\":%s,\"ask\":%s,\"flags\":%u}",
      CommonFields("TICK"),
      tick.time_msc,
      DoubleToString(tick.bid, _Digits),
      DoubleToString(tick.ask, _Digits),
      (uint)tick.flags
   );
   return WriteRecord(line);
  }

bool EmitHeartbeat()
  {
   const string line = StringFormat(
      "%s,\"last_tick_time_msc\":%I64d}",
      CommonFields("BRIDGE_HEARTBEAT"),
      g_last_tick_time_msc
   );
   return WriteRecord(line);
  }

int OnInit()
  {
   const ENUM_ACCOUNT_TRADE_MODE mode = (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   if(mode != ACCOUNT_TRADE_MODE_DEMO)
     {
      Print("FMP Phase 8 bridge refused: demo account required");
      return INIT_FAILED;
     }

   if(_Symbol != BRIDGE_SYMBOL)
     {
      Print("FMP Phase 8 bridge refused: USDJPY chart required");
      return INIT_FAILED;
     }

   g_server = AccountInfoString(ACCOUNT_SERVER);
   if(!AllowedServer(g_server))
     {
      Print("FMP Phase 8 bridge refused: unapproved demo server");
      return INIT_FAILED;
     }

   const long login = AccountInfoInteger(ACCOUNT_LOGIN);
   g_account_fingerprint = Sha256Text(StringFormat("%I64d", login));
   g_session_id = MakeSessionId(login, g_server);
   if(StringLen(g_account_fingerprint) != 64 || StringLen(g_session_id) != 64)
     {
      Print("FMP Phase 8 bridge refused: identity hashing failed");
      return INIT_FAILED;
     }

   FileDelete(BRIDGE_FILE, FILE_COMMON);
   g_file = FileOpen(
      BRIDGE_FILE,
      FILE_WRITE | FILE_TXT | FILE_ANSI | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE,
      0,
      CP_UTF8
   );
   if(g_file == INVALID_HANDLE)
     {
      Print("FMP Phase 8 bridge refused: transport file unavailable");
      return INIT_FAILED;
     }

   if(!EmitBridgeStart())
     {
      FileClose(g_file);
      g_file = INVALID_HANDLE;
      Print("FMP Phase 8 bridge refused: startup record write failed");
      return INIT_FAILED;
     }

   if(!EventSetTimer(HEARTBEAT_SECONDS))
     {
      FileClose(g_file);
      g_file = INVALID_HANDLE;
      Print("FMP Phase 8 bridge refused: heartbeat timer unavailable");
      return INIT_FAILED;
     }

   return INIT_SUCCEEDED;
  }

void OnTick()
  {
   if(g_file == INVALID_HANDLE)
      return;

   MqlTick tick;
   if(!SymbolInfoTick(BRIDGE_SYMBOL, tick))
      return;
   if(tick.time_msc <= 0)
      return;
   if(!MathIsValidNumber(tick.bid) || !MathIsValidNumber(tick.ask))
      return;
   if(tick.bid <= 0.0 || tick.ask <= 0.0 || tick.ask < tick.bid)
      return;

   if(EmitTick(tick))
      g_last_tick_time_msc = tick.time_msc;
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
