# Apache ActiveMQ Classic + Artemis 2.x AMQP Sender Tool

![image](https://github.com/user-attachments/assets/e3f649eb-94b5-4f0f-8207-dd4d5c88fec7)

A simple Python based GUI client for sending messages via AMQP protocol to **Apache ActiveMQ Classic/Artemis 2.x** message brokers. Designed for testing and debugging message queues with support for text and file attachments.

---

## Features
- **AMQP 1.0 Protocol Support**: Compatible with Apache ActiveMQ Classic and Artemis 2.x
- **Message Types**:
  - Text messages
  - File attachments (auto-encoded to base64)
- **Message Metadata**:
  - Unique message IDs
  - Timestamps
- **Connection Management**:
  - Custom host/port configuration
  - Custom queue name configuration
- **Logging**: Detailed send/error logs with auto-scroll

---

## Connection Parameters
| Field      | Default Value     | Description                |
|------------|-------------------|----------------------------|
| Server     | `127.0.0.1:61716` | Broker IP/hostname:port    |
| Username   | -                 | (Optional) Broker username |
| Password   | -                 | (Optional) Broker password |
| Queue      | `test_queue`      | Target queue name          |

---

## Usage
1. **Send Text Messages**:
   - Enter message in the text area
   - Click **Send Message**

2. **Send Files**:
   - Click **Attach File** to select a file
   - File name appears next to the button
   - Click **✕** to remove attachment
   - Click **Send Message** (file will be auto-encoded to base64)

3. **Logs**:
   - Successful sends show:
     ```
     The message was successfully sent to [queue]
     Message ID: [UUID]
     Timestamp: [YYYY-MM-DD HH:MM:SS]
     ```
   - Errors display detailed information

---

## Installation
1. **Requirements**:
   - Python 3.6+
   - `pip install python-qpid-proton tkinter`

2. **Run**:
   - `python apache_amqp_client_[version].py`
   or
   just download and run .exe for Windows {Python libs not required}
