import asyncio
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse
import model
import json


app = FastAPI()


def validate_input(data):
    keys = ['N', 'P', 'K', 'temp', 'humidity', 'rainfall']

    for k in keys:
        float(data[k])

    if data['nature'] not in ['acidic', 'neutral', 'alkaline']:
        raise ValueError('Invalid value for field nature')


@app.get('/api/cropr')
async def crop_r(N: float, P: float, K: float, temp: float, humidity: float, rainfall: float, nature: str):
    if nature not in ['acidic', 'neutral', 'alkaline']:
        return JSONResponse({
            'm': 'Invalid nature provided, valid values are [acidic, neutral, alkaline]'
        },
            status_code=400
        )
    prediction = await asyncio.get_running_loop().run_in_executor(None, model.predict, N, P, K, temp, humidity, rainfall, nature)
    return {'prediction': str(prediction)}


@app.post('/api/cropr')
async def crop_recommendation(request: Request):
    try:
        data = await request.json()
        try:
            validate_input(data)
        except KeyError as e:
            key = e.args,
            return JSONResponse(
                content={
                    'm': f'Key not specified {key}'
                },
                status_code=400
            )
        except ValueError as e:
            return JSONResponse(
                content={
                    'm': str(e)
                },
                status_code=400
            )
    except json.decoder.JSONDecodeError:
        return JSONResponse(content={'m': 'invalid json payload'}, status_code=400)

    result = await asyncio.get_running_loop().run_in_executor(None, model.predict, *data.values())

    print(await request.body())
    return {'prediction': str(result)}