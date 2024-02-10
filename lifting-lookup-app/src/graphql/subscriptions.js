/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onCreateVIPLifterSubscription = /* GraphQL */ `
  subscription OnCreateVIPLifterSubscription(
    $filter: ModelSubscriptionVIPLifterSubscriptionFilterInput
    $owner: String
  ) {
    onCreateVIPLifterSubscription(filter: $filter, owner: $owner) {
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
export const onUpdateVIPLifterSubscription = /* GraphQL */ `
  subscription OnUpdateVIPLifterSubscription(
    $filter: ModelSubscriptionVIPLifterSubscriptionFilterInput
    $owner: String
  ) {
    onUpdateVIPLifterSubscription(filter: $filter, owner: $owner) {
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
export const onDeleteVIPLifterSubscription = /* GraphQL */ `
  subscription OnDeleteVIPLifterSubscription(
    $filter: ModelSubscriptionVIPLifterSubscriptionFilterInput
    $owner: String
  ) {
    onDeleteVIPLifterSubscription(filter: $filter, owner: $owner) {
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
