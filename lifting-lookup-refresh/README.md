# Lifting Lookup Refresh Lambda

This is a Lambda function that periodically refreshes lifter data from LiftingCast and sends notifications to VIP subscribers.


## Required IAM Permissions

The Lambda function's execution role needs the following permissions:

- `dynamodb:Scan`
- `dynamodb:PutItem`
- `dynamodb:DeleteItem`
- `ses:SendEmail`

## Environment Variables

The following environment variables must be set in the Lambda function configuration:

- `AWS_DYNAMO_LIFTER_TABLE_NAME`: Name of the DynamoDB table storing lifter data
- `AWS_DYNAMO_LIFTER_UPDATE_TABLE_NAME`: Name of the DynamoDB table storing update history
- `AWS_DYNAMO_VIP_LIFTER_SUBSCRIPTION_TABLE_NAME`: Name of the DynamoDB table storing VIP subscriptions 