# frozen_string_literal: true

# Merges optional environment variables into site.config["analytics"] after
# _config.yml is loaded. Safe defaults in _config.yml stay in effect when env
# vars are unset. Disabled when Jekyll runs with safe mode (no local plugins).
module Jekyll
  module AnalyticsEnvOverride
    TRUTHY = %w[1 true yes on].freeze

    module_function

    def truthy_env?(value)
      return nil if value.nil?

      s = value.to_s.strip
      return nil if s.empty?

      TRUTHY.include?(s.downcase)
    end

    def stringify_keys(hash)
      return {} unless hash.is_a?(Hash)

      hash.each_with_object({}) { |(k, v), out| out[k.to_s] = v }
    end

    def merge_analytics!(site)
      raw = site.config["analytics"]
      raw = {} unless raw.is_a?(Hash)

      ga4 = stringify_keys(raw["ga4"] || raw[:ga4] || {})
      plausible = stringify_keys(raw["plausible"] || raw[:plausible] || {})

      %w[JEKYLL_ANALYTICS_GA4_MEASUREMENT_ID GA4_MEASUREMENT_ID].each do |key|
        val = ENV[key]
        next if val.nil? || val.strip.empty?

        ga4["measurement_id"] = val.strip
        break
      end

      %w[JEKYLL_ANALYTICS_GA4_ENABLED GA4_ANALYTICS_ENABLED].each do |key|
        next unless ENV.key?(key)

        t = truthy_env?(ENV[key])
        ga4["enabled"] = t unless t.nil?
        break
      end

      %w[JEKYLL_ANALYTICS_PLAUSIBLE_DOMAIN PLAUSIBLE_DOMAIN].each do |key|
        val = ENV[key]
        next if val.nil? || val.strip.empty?

        plausible["domain"] = val.strip
        break
      end

      %w[JEKYLL_ANALYTICS_PLAUSIBLE_SCRIPT_SRC PLAUSIBLE_SCRIPT_SRC].each do |key|
        val = ENV[key]
        next if val.nil? || val.strip.empty?

        plausible["script_src"] = val.strip
        break
      end

      %w[JEKYLL_ANALYTICS_PLAUSIBLE_ENABLED PLAUSIBLE_ANALYTICS_ENABLED].each do |key|
        next unless ENV.key?(key)

        t = truthy_env?(ENV[key])
        plausible["enabled"] = t unless t.nil?
        break
      end

      site.config["analytics"] = {
        "ga4" => ga4,
        "plausible" => plausible
      }
    end
  end
end

Jekyll::Hooks.register :site, :after_init do |site|
  Jekyll::AnalyticsEnvOverride.merge_analytics!(site)
end
