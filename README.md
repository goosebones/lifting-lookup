# Lifting Lookup

## Description

This application is for looking up lifters that are currently registered for meets on liftingcast.com . It also shows lifters that have competed at recent meets.

Here are some use cases for this app:

- Looking to see if a lifter is registered for an upcoming meet on LiftingCast
- Searching for a lifters may have recently competed at a meet that used LiftingCast
- Searching for an upcoming competition
- Searching for a recent competition

## Code Breakdown

### lifting-lookup-app

This is a Vue.js application to display the lifters who are currently registered for meets on LiftingCast. It used Vuetify to make it look pretty.

### lifting-lookup-lambda

This serves as an API for fetching lifters. It is meant to be deployed as an AWS Lambda function.

### lifting-lookup-refresh

Data for the application can be refreshed using this code. This code will get data from from liftingcast.com and write it to a DynamoDB table.

This code is meant to be deployed using an AWS Lambda Function.
