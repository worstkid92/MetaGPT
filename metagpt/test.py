import asyncio
from metagpt.logs import logger
from metagpt.roles import Designer,ValidationEngineer
from metagpt.actions import UserRequirement
from metagpt.environment import Environment
from metagpt.schema import Message
from metagpt.const import MESSAGE_ROUTE_TO_ALL

import os
import json
import sys
import datetime


async def run(msg:str,output_path: str):
    env = Environment()
    env.add_roles(
        [
            Designer(output_path),
            ValidationEngineer()
        ]
    )

    env.publish_message(
        Message(role="Human", content=msg, cause_by=UserRequirement, send_to=MESSAGE_ROUTE_TO_ALL),
    )


    n_round = 3
    while n_round > 0:
        if env.is_idle:
            logger.info("All roles are idle.")
            break
        """logger.info("===========status check============")
        for r in env.roles.values():
            logger.info(r.profile,r.is_idle)
            if r.is_idle:logger.info(f"{r.profile} is idle")"""
        n_round -= 1
        await env.run()
        logger.info(f"max {n_round=} left.")

async def f(file_path:str,output_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            datas = json.load(file)
        
        for data in datas:
            logger.info(data['input'])
            await run(data['input'],output_path)
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while processing file {file_path}: {e}")

    

async def main(benchmark_dataset_path):
    logger.info("test test test!!!")
    #dir_path = '/mnt/dataset/development_advice/benchmark'
    #dir_path = '/mnt/codes/shroud/work/workspace'
    #python /mnt/codes/shroud/work/MetaGPT/metagpt/test.py '/mnt/codes/shroud/work/workspace'

    output_path = '/mnt/codes/shroud/work/output'

    
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%m-%d_%H:%M:%S")

    output_path = output_path + '/' + formatted_time

    for file_name in os.listdir(benchmark_dataset_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(benchmark_dataset_path, file_name)
            await f(file_path,output_path)
    

    


if __name__ == '__main__':
    # 传入的是数据集目录的地址
    asyncio.run(main(sys.argv[1]))