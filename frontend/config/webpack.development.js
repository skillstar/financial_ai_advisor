const HtmlWebpackPlugin = require('html-webpack-plugin');  
const { resolve, join } = require('path');  
const FriendlyErrorsWebpackPlugin = require('@soda/friendly-errors-webpack-plugin');  
const notifier = require('node-notifier');  

const port = 3003;  

module.exports = {  
  mode: 'development',  
  devtool: 'eval-cheap-module-source-map',  
  
   devServer: {   
    // CSP头已注释，保持注释状态  
    host: 'localhost',  
    port,  
    open: true,  
    historyApiFallback: true,  
    static: {  
      directory: join(__dirname, '../public'),  
    },  
    hot: true,  
    compress: true,  
    client: {  
      overlay: {  
        errors: true,  
        warnings: false,  
      },  
      progress: true,  
    },  
    proxy: [  
      {  
        context: ['/ws/analysis'],  
        target: 'http://localhost:8000',  
        ws: true,  
        changeOrigin: true  
      },  
      {  
        context: ['/api'], // 添加API代理规则  
        target: 'http://localhost:8000',  
        changeOrigin: true  
      }  
    ]  
  },  

  stats: 'errors-only',  
  
  output: {  
    publicPath: '/',  
    filename: 'scripts/[name].bundle.js',  
    assetModuleFilename: 'images/[name].[ext]',  
  },  

  plugins: [  
    new HtmlWebpackPlugin({  
      title: 'My App',  
      filename: 'index.html',  
      template: resolve(__dirname, '../src/index-dev.html'),  
      favicon: './public/favicon.ico',  
      inject: true,  
    }),  
    new FriendlyErrorsWebpackPlugin({  
      compilationSuccessInfo: {  
        messages: [`🚀 Your application is running here http://localhost:${port}`],  
        notes: ['💊 构建信息请及时关注窗口右上角'],  
      },  
      onErrors: (severity, errors) => {  
        if (severity !== 'error') return;  
        
        const error = errors[0];  
        notifier.notify({  
          title: '👒 Webpack Build Error',  
          message: `${severity}: ${error.name}`,  
          subtitle: error.file || '',  
          icon: join(__dirname, 'icon.png'),  
        });  
      },  
      clearConsole: true,  
    }),  
  ],  
};  