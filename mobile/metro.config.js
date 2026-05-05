/**
 * Metro configuration for React Native with code obfuscation
 * https://facebook.github.io/metro/docs/configuration
 *
 * @type {import('metro-config').MetroConfig}
 */

const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Production optimizations
if (process.env.NODE_ENV === 'production') {
  // Enable minification
  config.transformer = {
    ...config.transformer,
    minifierConfig: {
      keep_classnames: false, // Obfuscate class names
      keep_fnames: false, // Obfuscate function names
      mangle: {
        toplevel: true, // Mangle top-level variable and function names
        keep_classnames: false,
        keep_fnames: false,
      },
      compress: {
        drop_console: true, // Remove console.log statements
        drop_debugger: true, // Remove debugger statements
        pure_funcs: ['console.log', 'console.info', 'console.debug'], // Remove specific console methods
        passes: 3, // Multiple compression passes for better results
      },
      output: {
        comments: false, // Remove all comments
        beautify: false, // Don't beautify output (makes it harder to read)
      },
    },
  };
}

module.exports = config;
