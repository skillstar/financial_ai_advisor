const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const { join, resolve } = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');  
module.exports = {
  output: {
    path: join(__dirname, '../dist'),
    publicPath: '/',
    filename: 'scripts/[name].[contenthash:5].bundule.js',
    assetModuleFilename: 'images/[name].[contenthash:5][ext]',
  },
  performance: {
    maxAssetSize: 250000, // 最大资源大小250KB
    maxEntrypointSize: 250000, // 最大入口资源大小250KB
    hints: 'warning', // 超出限制时只给出警告
  },
  optimization: {
    minimize: true,
    minimizer: [
      //css多线程压缩
      new CssMinimizerPlugin({
        parallel: true,
      }),
      new TerserPlugin({
        parallel: true, // 启用多线程压缩
        terserOptions: {
          compress: {
            drop_console: true,
          },
          format: {
            comments: false, // 移除所有注释
          },
        },
        extractComments: false, // 不将注释提取到单独的文件中
      }),
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: 'Yideng',
      filename: 'index.html',
      //开发环境的html 上线环境html
      template: resolve(__dirname, '../src/index-prod.html'),
      favicon: './public/favicon.ico',
    }),
       new CopyWebpackPlugin({  
      patterns: [  
        { from: 'public', to: '' }  
      ]  
    }) 
  ],
};
