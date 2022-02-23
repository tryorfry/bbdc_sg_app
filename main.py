from fastapi import FastAPI

import os
import bbdc

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/api/book/show_tpds_slots')
async def show_tpds_slots():
    robo = bbdc.Bbdc(username=os.environ['username'], password=os.environ['password'])
    robo.login()
    print(robo.member_info)
    robo.tp_simulater_booking()
    robo.driver.quit()

    return {'message': 'Successfully found the info of tpds slots and screenshot send'}

