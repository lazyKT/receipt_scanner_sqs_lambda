# Serverless framework with python

## Work flow
- `AWS API Gateway -> lambda -> sqs -> lambda -> database`
- Image processing (for tesseract) requests are sent to lambda (`lambda1`) via API Gateway
- `lambda1` receive the requests send to *AWS SQS FIFO* and return response to client
- *AWS SQS FIFO* triggers another lambda (`lambda2`) to process the tesseract ocr operations

## Motive
- For scaling and performance, API Gateway lambda (`lambda1`) does not wait for the image processing to finish, sends the request to *AWS SQS FIFO* instead and immediately response back to the client with the `SQS Message Id` (which will be used later for request polling to check if the data is ready or not)
- *AWS SQS FIFO* to controll the number of `lambda2` instances launched by AWS (to perform ocr) and avoid sudden spike in traffic with maximun of 10 items per batch
- The second lambda (`lambda2`) perform ocr and save the processed data in database.

## How to run
- to run locally
  `serverless invoke local -f send_queue -p tests/mockData/lambda_event.json`
  `serverless invoke local -f ocr -p tests/mockData/sqs_fifo_event.json`

- to deploy
  `serverless deploy --stage dev`


## Testing
- Unit testing
  `pytest`
- Load testing
  `artillery run-lambda --region ap-southeast-1 tests/load-test/warm-up.yml`