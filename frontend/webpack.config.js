const merge = require('webpack-merge');  
const argv = require('yargs-parser')(process.argv.slice(2));  
const { resolve } = require('path');  
const MiniCssExtractPlugin = require('mini-css-extract-plugin');  
const Dotenv = require('dotenv-webpack');  
const { CleanWebpackPlugin } = require('clean-webpack-plugin');  
const { ThemedProgressPlugin } = require('themed-progress-plugin');  

const _mode = argv.mode || 'development';  
const _mergeConfig = require(`./config/webpack.${_mode}.js`);  
const _modeflag = _mode === 'production';  

const webpackBaseConfig = {  
  entry: {  
    main: resolve('src/index.tsx'),  
  },  
  
  output: {  
    path: resolve(process.cwd(), 'dist'),  
  },  
  
  module: {  
    rules: [  
      {  
        test: /\.(ts|tsx)$/,  
        exclude: /node_modules/,  
        use: 'swc-loader',  
      },  
      {  
        test: /\.(eot|woff|woff2|ttf|svg|png|jpg)$/i,  
        type: 'asset/resource',  
      },  
      {  
        test: /\.css$/i,  
        include: [resolve(__dirname, 'src')],  
        use: [  
          _mode === 'development' ? 'style-loader' : MiniCssExtractPlugin.loader,  
          {   
            loader: 'css-loader',   
            options: {   
              importLoaders: 1   
            }   
          },  
          'postcss-loader',  
        ],  
      },  
    ],  
  },  

  resolve: {  
    alias: {  
     '@': resolve('src/'),
      '@components': resolve('src/components'),
      '@hooks': resolve('src/hooks'),
      '@pages': resolve('src/pages'),
      '@layouts': resolve('src/layouts'),
      '@assets': resolve('src/assets'),
      '@states': resolve('src/states'),
      '@service': resolve('src/service'),
      '@utils': resolve('src/utils'),
      '@lib': resolve('src/lib'),
      '@constants': resolve('src/constants'),
      '@connectors': resolve('src/connectors'),
      '@abis': resolve('src/abis'),
      '@types': resolve('src/types')
    },  
    extensions: ['.js', '.ts', '.tsx', '.jsx', '.css'],  
  },  

  plugins: [  
    new CleanWebpackPlugin(),  
    new MiniCssExtractPlugin({  
      filename: _modeflag ? 'styles/[name].[contenthash:5].css' : 'styles/[name].css',  
      chunkFilename: _modeflag ? 'styles/[name].[contenthash:5].css' : 'styles/[name].css',  
    }),  
    new Dotenv(),  
    new ThemedProgressPlugin()
  ].filter(Boolean),  
};  

module.exports = merge.default(webpackBaseConfig, _mergeConfig);  