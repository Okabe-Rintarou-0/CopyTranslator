# CopyTranslator

Translate when you copy.

## Features

+ Support linux & windows
+ Based on `Baidu`, `Youdao` and `Bing` apis.
+ Sometimes it will log `ERROR baidu sdk error: 1022 msg: 访问出现异常，请刷新后重试！`, due to some unknown internal error in
  `Baidu` apis. It is **OK**, because the copyTranslator will try other apis.

## How to

1. Create environment.
    ```shell script
    conda create -n copy_trans python=3.7
    conda activate copy_trans
    ``` 
2. Download dependencies.
    ```shell script
    pip install -r requirements
    ``` 
    For linux, need run `./linux_setup.sh`
3. Run it.
    ```shell script
    python run.py
    ```
4. Copy and translate.

## Screenshots

![screenshot](./images/screenshot.png)
