/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getVIPLifterSubscription = /* GraphQL */ `
  query GetVIPLifterSubscription($id: ID!) {
    getVIPLifterSubscription(id: $id) {
      id
      subscriber_email
      subscription_list
      createdAt
      updatedAt
      owner
      __typename
    }
  }
`;
export const listVIPLifterSubscriptions = /* GraphQL */ `
  query ListVIPLifterSubscriptions(
    $filter: ModelVIPLifterSubscriptionFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listVIPLifterSubscriptions(
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
      items {
        id
        subscriber_email
        subscription_list
        createdAt
        updatedAt
        owner
        __typename
      }
      nextToken
      __typename
    }
  }
`;
