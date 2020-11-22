<div align="center">

# Beta-monitor :anchor: 

</div>

**Beta Monitor**是一个基于 hbb2/hbb-core>和flask的**Beta设备状态监控系统**，旨在使用Web页面的方式管理部分beta设备，并使用自动化的方式对相应的设备进行信息收集及展示

## Run the Beta Monitor system


### Requirement

1. MySQL server
2. Python2.7
3. Flask

### Before Start
##### In folder "beta-monitor":

1. Install HBB2.0 framework and some other python libs

    ```bash
    pip install -r requirements.txt
    ```

1. Install Mysql, create right user account and database "beta_monitor" according to file "app/db.py"

1. Create or Update tables in "beta_monitor"

    ```bash
    $ alembic upgrade head
    ```

### Start
1. 如果想利用flask自带的web server简单部署，则进入beta-monitor目录执行supervisord -c supervisord.conf即可

   ```bash
   root@ubuntu16-10:/home/beta-monitor#supervisord -c supervisord.conf
   ```
2. 如果想借助其他更专业的web server和uwsgi部署，请参考相关的部署文档