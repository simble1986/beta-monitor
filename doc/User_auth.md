# Beta Monitor支持登陆

## 需求说明

Beta Monitor支持登陆认证及权限控制

1. 用户注册
2. 用户登陆
3. 用户注销
4. 需要有一个用户列表，对所有用户进行展示
5. 设备列表、project列表、修改设备状态、创建任务等都将受到认证模块控制

## 主要页面

* 登陆登出出页面
* 用户注册页面

## 数据库相关

### 用户数据表

id | username | email | password | group
--- | --- | --- | --- | ---
1 | bqi | bqi@testsite.com | Si87zHasgks | admin

### hs_projects表

修改owner由email变为user_id

### hs_devices表

1. 修改owner由email变为user_id
2. 修改follower为一个由user_id组成的字符串

**注：当删除一个user时，是否需要遍历所有设备待考虑**

### hs_rss表

修改email为user_id，可以为一个以`,`分隔的字符串，当删除user时，

## 功能说明

### Project

1. project将具有用户属性，只有admin的user和属主才可以修改、删除当前project
2. 当创建一个project时，属主为当前用户
3. 创建设备时，project列表仅显示当前用户的project及default project

### Device

1. 设备具有用户属性，只有admin和设备的属主才可以修改、删除当前设备
2. 对于一个设备，任何人可下发任务
3. 增加显示所有设备列表的按钮，但默认状况下，仅显示default project和属于自己的设备

## 用户管理

### 用户查看

1. 所有人都可以查看用户列表及角色
2. 用户列表最后一行为可操作选项，用户只能修改自己的
3. admin用户可以修改任何用户，同时可以设置另外一个普通用户为admin，暂不支持降级操作
4. 支持一键reset password为beta
5. 用户列表包含以下内容

ID | User Name | Email | Devices | Projects | Group | Action
--- | --- | --- | --- | --- | --- | ---
1 | bqi | bqi@testsite.com | 3 | 2 | Admin | Modify/Set as Admin/Reset Password

### 用户创建

1. 创建用户时，需要先查询用户名是否已经存在
2. 密码需要输入两次来做验证
3. 创建用户后，可以以邮件的形式通知用户，用户名及密码
4. 密码以加密方式存储

### 用户修改

1. 原则上，用户不可以修改自己的user_name
2. 用户可以修改自己的密码
3. 用户可以修改自己的email
4. admin用户可以修改用户的密码

### 用户注销

1. 当查询到用户有设备时，不允许用户注销
2. 当用户注销时，如果没有设备，但有project，则project自动删除
3. 需要有两步删除提示
4. 


用户权限，会话保持 —— 程磊

数据库 —— 江锡

Windows —— yilian ，齐博， hbb-core\hbb-bds

RSS —— 林涛

星羽 —— 用户列表，注册页面、登陆

project权限控制 —— 杜晶

设备权限控制 —— 陈婷

后台增加日报任务调度 —— 杜晶

license过期时间 —— 林涛