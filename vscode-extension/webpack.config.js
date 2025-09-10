const path = require('path');
const webpack = require('webpack');

/** @type {import('webpack').Configuration} */
const config = {
    target: 'node',
    mode: 'production',
    
    entry: {
        extension: './src/extension.ts',
        server: './src/server.ts'
    },
    
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js',
        libraryTarget: 'commonjs2'
    },
    
    externals: {
        vscode: 'commonjs vscode'
    },
    
    resolve: {
        extensions: ['.ts', '.js']
    },
    
    module: {
        rules: [
            {
                test: /\.ts$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'ts-loader'
                    }
                ]
            }
        ]
    },
    
    optimization: {
        minimize: true
    },
    
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('production')
        })
    ]
};

module.exports = config;