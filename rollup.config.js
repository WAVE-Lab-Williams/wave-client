// Rollup configuration for WAVE JavaScript client
export default [
  // ES6 Module build
  {
    input: 'javascript/src/wave-client.js',
    output: {
      file: 'javascript/dist/wave-client.esm.js',
      format: 'es',
      sourcemap: true
    }
  },
  // UMD build for <script> tag usage
  {
    input: 'javascript/src/wave-client.js',
    output: {
      file: 'javascript/dist/wave-client.umd.js',
      format: 'umd',
      name: 'WaveClient',
      sourcemap: true,
      exports: 'named'
    }
  },
  // Minified UMD build
  {
    input: 'javascript/src/wave-client.js',
    output: {
      file: 'javascript/dist/wave-client.min.js',
      format: 'umd',
      name: 'WaveClient',
      sourcemap: true,
      compact: true,
      exports: 'named'
    },
    plugins: [
      // Add terser for minification when building for production
      process.env.NODE_ENV === 'production' && (await import('@rollup/plugin-terser')).default()
    ].filter(Boolean)
  }
];