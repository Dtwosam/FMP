#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"

inputs = ARGV.empty? ? [".github/workflows"] : ARGV
paths = inputs.flat_map do |input|
  if File.directory?(input)
    Dir[File.join(input, "**", "*.{yml,yaml}")]
  else
    [input]
  end
end.uniq.sort

if paths.empty?
  warn "no workflow YAML files found"
  exit 2
end

failed = false
paths.each do |path|
  begin
    Psych.parse_file(path)
  rescue Errno::ENOENT => e
    warn "#{path}: #{e.message}"
    failed = true
  rescue Psych::SyntaxError => e
    warn "#{path}:#{e.line}:#{e.column}: #{e.problem}"
    failed = true
  end
end

exit(failed ? 1 : 0)
