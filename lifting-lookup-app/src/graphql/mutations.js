/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createVIPLifterSubscription = /* GraphQL */ `
  mutation CreateVIPLifterSubscription(
    $input: CreateVIPLifterSubscriptionInput!
    $condition: ModelVIPLifterSubscriptionConditionInput
  ) {
    createVIPLifterSubscription(input: $input, condition: $condition) {
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
export const updateVIPLifterSubscription = /* GraphQL */ `
  mutation UpdateVIPLifterSubscription(
    $input: UpdateVIPLifterSubscriptionInput!
    $condition: ModelVIPLifterSubscriptionConditionInput
  ) {
    updateVIPLifterSubscription(input: $input, condition: $condition) {
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
export const deleteVIPLifterSubscription = /* GraphQL */ `
  mutation DeleteVIPLifterSubscription(
    $input: DeleteVIPLifterSubscriptionInput!
    $condition: ModelVIPLifterSubscriptionConditionInput
  ) {
    deleteVIPLifterSubscription(input: $input, condition: $condition) {
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
