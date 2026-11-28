import {fileURLToPath} from 'node:url'
export default {
  root:fileURLToPath(new URL('.',import.meta.url)),base:'./',publicDir:false,
  build:{outDir:'web',assetsInlineLimit:0,rolldownOptions:{output:{
    entryFileNames:'assets/study.js',assetFileNames:'assets/[name][extname]'
  }}}
}
