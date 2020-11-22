# !/usr/bin/env python
# encoding: utf-8
#
# Author: lcheng
#
import numpy
from common import *


# 获取指定device的历史数据json文件
@app.route('/detail_json/<id>')
def get_detail_json(id):
    now = int(time.time())
    data = betaDeviceDetail().getItemsByDid(device_id=id, start_time=now-86400, end_time=now)
    return agg_data(data, start_time=now-86400, end_time=now,  period=3600)


def agg_data(data, start_time, end_time, period):

    """ 把数据库数据按指定周期进行聚合, end_time之前没有数据的周期填充0 """

    result = {"xData": [],
              "datasets": [{"name": "CPU", "data": [], "unit": "%", "type": "line", "valueDecimals": 1},
                           {"name": "Memory", "data": [], "unit": "%", "type": "line", "valueDecimals": 1},
                           {"name": "Session", "data": [], "unit": "个", "type": "area", "valueDecimals": 0}
                          ]
             }

    cur_group = []
    cur_start_time = start_time
    cur_end_time = start_time+period
    for i in data:
        # 新数据在当前时间段内
        if cur_start_time<=i['create_time']<cur_end_time:
            cur_group.append(i)
        # 新数据不在当前时间段内，则汇总当前时间段数据，判断新数据是否在下个时间段内
        else:
            if cur_group:
                avg_cpu = numpy.mean([v['cpu'] for v in cur_group])
                avg_mem = numpy.mean([v['mem'] for v in cur_group])
                avg_sess = numpy.mean([v['sess'] for v in cur_group])
            else:
                avg_cpu = avg_mem = avg_sess = 0

            result['xData'].append(cur_end_time*1000)
            result['datasets'][0]['data'].append(avg_cpu)
            result['datasets'][1]['data'].append(avg_mem)
            result['datasets'][2]['data'].append(avg_sess)

            cur_group = []
            # 时间段不断后移，直到找到新数据所在的时间段
            while True:
                cur_start_time, cur_end_time = cur_end_time, cur_end_time+period
                if cur_start_time<=i['create_time']<cur_end_time:
                    cur_group.append(i)
                    break
                else:
                    result['xData'].append(cur_end_time*1000)
                    result['datasets'][0]['data'].append(0)
                    result['datasets'][1]['data'].append(0)
                    result['datasets'][2]['data'].append(0)
    else:
        # 数据迭代完后，要先把当前时间段的数据汇总
        if cur_group:
            avg_cpu = numpy.mean([v['cpu'] for v in cur_group])
            avg_mem = numpy.mean([v['mem'] for v in cur_group])
            avg_sess = numpy.mean([v['sess'] for v in cur_group])
        else:
            avg_cpu = avg_mem = avg_sess = 0

        result['xData'].append(cur_end_time*1000)
        result['datasets'][0]['data'].append(avg_cpu)
        result['datasets'][1]['data'].append(avg_mem)
        result['datasets'][2]['data'].append(avg_sess)
        # 如果数据迭代完，但还没到达结束时间，应该把之后各时间段的数据填充0
        while cur_end_time<end_time:
            cur_start_time, cur_end_time = cur_end_time, cur_end_time+period
            result['xData'].append(cur_end_time*1000)
            result['datasets'][0]['data'].append(0)
            result['datasets'][1]['data'].append(0)
            result['datasets'][2]['data'].append(0)

    return json.dumps(result, indent=4)

