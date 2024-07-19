import threading  # 导入线程模块，用于创建和管理线程
import requests   # 导入requests库，用于发送HTTP请求

# 定义一个函数download_chunk，用于下载指定URL的文件块
def download_chunk(url, start, end, filename, lock):
    headers = {'Range': f'bytes={start}-{end}'}  # 设置请求头，指定要下载的文件块范围
    try:
        response = requests.get(url, headers=headers, timeout=10)  # 发送GET请求，获取文件块内容
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常
        chunk = response.content  # 获取响应内容（即文件块数据）
        with lock:  # 使用锁确保线程安全地写入文件
            with open(filename, 'rb+') as file:  # 以二进制读写模式打开文件
                file.seek(start)  # 将文件指针移动到指定的起始位置
                file.write(chunk)  # 写入文件块数据
    except requests.RequestException as e:  # 捕获请求异常
        print(f"Error downloading {url} chunk {start}-{end}: {e}")  # 打印错误信息

# 定义一个函数download_file，用于下载整个文件
def download_file(url, num_threads):
    response = requests.head(url)  # 发送HEAD请求，仅获取响应头信息
    file_size = int(response.headers['Content-Length'])  # 从响应头中获取文件大小
    chunk_size = file_size // num_threads  # 计算每个线程需要下载的文件块大小

    # 创建一个锁对象，用于同步线程间的文件操作
    lock = threading.Lock()

    # 初始化输出文件，填充零字节（可选，但有助于进度跟踪）
    with open('output_file', 'wb') as file:
        file.seek(file_size - 1)  # 将文件指针移动到文件末尾
        file.write(b'\0')  # 写入一个零字节
        file.truncate()  # 截断文件，使其大小与实际文件大小一致

    threads = []  # 创建一个空列表，用于存储线程对象
    for i in range(num_threads):  # 遍历线程数量
        start = i * chunk_size  # 计算当前线程应下载的文件块的起始位置
        end = min(start + chunk_size - 1, file_size - 1)  # 计算当前线程应下载的文件块的结束位置
        thread = threading.Thread(target=download_chunk, args=(url, start, end, 'output_file', lock))  # 创建线程对象
        thread.start()  # 启动线程
        threads.append(thread)  # 将线程对象添加到列表中

    for thread in threads:  # 遍历线程列表
        thread.join()  # 等待线程完成

    print('Download complete.')  # 打印下载完成的消息

# 示例用法：下载一个4MB大小的文件，使用4个线程进行分块下载
download_file('https://download-porter.hoyoverse.com/download-porter/2024/06/04/GenshinImpact_install_202405121403.exe?trace_key=GenshinImpact_install_ua_76f6d3031721', 4)