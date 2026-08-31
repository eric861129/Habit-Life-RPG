param prefix string
param tags object

param budgetStartDate string = utcNow('yyyy-MM-01T00:00:00Z')
param budgetEndDate string = '2036-08-01T00:00:00Z'

@description('資源群組每月預算，單位固定為訂閱帳務幣別 TWD；NT$960 約為 US$30，並刻意稍早告警。')
@minValue(1)
param monthlyBudgetAmountTwd int = 960

@description('約 US$20 的實際費用預警，單位固定為訂閱帳務幣別 TWD。')
@minValue(1)
param usd20AlertBudgetAmountTwd int = 640

var ownerRoleId = '8e3af657-a8ff-443c-a75c-2fe8c4bcb635'

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: '${prefix}-budget-alerts'
  location: 'global'
  properties: {
    armRoleReceivers: [
      {
        name: 'Subscription Owner'
        roleId: ownerRoleId
        useCommonAlertSchema: true
      }
    ]
    automationRunbookReceivers: []
    azureAppPushReceivers: []
    azureFunctionReceivers: []
    emailReceivers: []
    enabled: true
    eventHubReceivers: []
    groupShortName: 'HLRBudget'
    itsmReceivers: []
    logicAppReceivers: []
    smsReceivers: []
    voiceReceivers: []
    webhookReceivers: []
  }
  tags: tags
}

resource monthlyBudget 'Microsoft.Consumption/budgets@2024-08-01' = {
  name: '${prefix}-monthly-budget'
  properties: {
    amount: monthlyBudgetAmountTwd
    category: 'Cost'
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: budgetStartDate
      endDate: budgetEndDate
    }
    notifications: {
      actual50: {
        contactEmails: []
        contactGroups: [
          actionGroup.id
        ]
        contactRoles: []
        enabled: true
        locale: 'zh-tw'
        operator: 'GreaterThanOrEqualTo'
        threshold: 50
        thresholdType: 'Actual'
      }
      actual80: {
        contactEmails: []
        contactGroups: [
          actionGroup.id
        ]
        contactRoles: []
        enabled: true
        locale: 'zh-tw'
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Actual'
      }
      actual100: {
        contactEmails: []
        contactGroups: [
          actionGroup.id
        ]
        contactRoles: []
        enabled: true
        locale: 'zh-tw'
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Actual'
      }
      forecasted100: {
        contactEmails: []
        contactGroups: [
          actionGroup.id
        ]
        contactRoles: []
        enabled: true
        locale: 'zh-tw'
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
      }
    }
  }
}

resource usd20AlertBudget 'Microsoft.Consumption/budgets@2024-08-01' = {
  name: '${prefix}-usd20-alert-budget'
  properties: {
    amount: usd20AlertBudgetAmountTwd
    category: 'Cost'
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: budgetStartDate
      endDate: budgetEndDate
    }
    notifications: {
      actual100: {
        contactEmails: []
        contactGroups: [
          actionGroup.id
        ]
        contactRoles: []
        enabled: true
        locale: 'zh-tw'
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Actual'
      }
    }
  }
}

output actionGroupName string = actionGroup.name
output budgetName string = monthlyBudget.name
output usd20AlertBudgetName string = usd20AlertBudget.name
