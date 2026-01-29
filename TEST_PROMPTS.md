# Test Prompts for Azure Updates MCP Server

## Overview

This document contains test prompts to exercise all 4 tools in the Azure Updates MCP server. The prompts are organized by category: basic functionality, edge cases, and real-world scenarios.

The server follows MCP best practices with a consolidated tool design:
- **ping** - Health check
- **azure_updates_search** - Flexible search with optional filters (query, category, status, date range, guid, limit)
- **azure_updates_summarize** - Statistical overview with optional parameters (weeks, top_n)
- **azure_updates_list_categories** - Category discovery

---

## 1. Basic Tool Testing (Individual Tools)

### ping
1. "Check if the Azure Updates MCP server is running"
2. "What's the health status of the Azure updates service?"

### azure_updates_search (basic listing)
3. "Show me the 5 most recent Azure updates"
4. "List the latest 20 Azure service updates"
5. "What are the newest Azure announcements?"

### azure_updates_search (keyword query)
6. "Search for Azure updates related to Kubernetes"
7. "Find any Azure updates mentioning 'security'"
8. "Search for 'storage' updates that are in preview"
9. "Look for Azure updates about 'AI' or 'machine learning'"

### azure_updates_list_categories
10. "What categories of Azure updates are available?"
11. "Show me all the Azure service categories and how many updates each has"

### azure_updates_search (category filter)
12. "Show me all updates for Azure Kubernetes Service"
13. "Get networking-related Azure updates"
14. "What's new in Azure SQL Database?"
15. "Find Compute updates that have launched"

### azure_updates_search (date range filter)
16. "Show me Azure updates from the last week"
17. "What Azure updates were published in January 2025?"
18. "Get all updates between 2025-01-01 and 2025-01-15"
19. "Show me retirements announced this month"

### azure_updates_search (by guid)
20. "Get the full details for this specific Azure update: [use a GUID from azure_updates_search]"

### azure_updates_search (status filter: preview)
21. "What Azure features are currently in preview?"
22. "Show me preview features for Azure Kubernetes Service"
23. "List all preview announcements, limit to 30"

### azure_updates_search (status filter: retirements)
24. "What Azure services are being retired?"
25. "Show me any retirement notices for storage services"
26. "Are there any upcoming Azure retirements I should know about?"

### azure_updates_summarize
27. "Give me an overview of recent Azure updates"
28. "What's the summary of Azure update activity?"
29. "Show me a dashboard of Azure updates"
30. "Summarize the last 2 weeks of Azure updates"
31. "Give me a high-level view of Azure announcements with top 5 categories"

---

## 2. Edge Cases and Error Handling

### Limit Parameter Testing
32. "Show me exactly 1 Azure update"
33. "List 100 Azure updates" (max limit)
34. "Show me 150 Azure updates" (exceeds max - should clamp to 100)

### Empty/No Results
35. "Search for Azure updates about 'xyznonexistent123'"
36. "Get updates for category 'FakeServiceThatDoesNotExist'"
37. "Show me Azure updates from 1990-01-01 to 1990-12-31" (no results expected)

### Invalid Input
38. "Get update details for GUID 'invalid-guid-12345'" (should return empty results)
39. "Search for updates with status 'InvalidStatus'" (should ignore invalid status)

### Date Range Edge Cases
40. "Show me Azure updates from 2025-12-31 to 2025-01-01" (end before start)
41. "Get updates from today only" (single day range)

### Combined Filters
42. "Search for 'Kubernetes' updates in the Compute category from last month that are in preview"
43. "Find retirement notices for Storage services from Q1 2025"

---

## 3. Real-World Scenarios

### Planning and Migration
44. "I'm planning to use Azure Kubernetes Service - what recent updates and previews should I know about?"
45. "We use Azure SQL Database - are there any retirements or breaking changes coming?"
46. "What Azure services have launched new features this month?"

### Security and Compliance
47. "Find any Azure security-related updates"
48. "Search for compliance or governance updates in Azure"
49. "What security features are in preview right now?"

### Multi-Tool Workflows
50. "First show me the categories, then get the top 10 updates for the most popular category"
51. "Get a summary of updates, then show me details on any retirements mentioned"
52. "Search for 'API' updates, then get full details on the most recent one"

### Specific Service Deep-Dives
53. "I need a complete picture of Azure Functions - show me recent updates, previews, and any retirements"
54. "What's happening with Azure OpenAI Service? Any new features or changes?"
55. "Give me all updates related to 'containers' or 'Kubernetes'"

### Status-Specific Queries
56. "What features launched in Azure this week?"
57. "Show me everything currently in development for Azure"
58. "Which Azure services have upcoming retirements in the database category?"

### Comparative/Trend Analysis
59. "Compare the number of updates across different Azure categories"
60. "What's the most active Azure service area based on recent updates?"

---

## 4. Natural Language Variations

These test how well the LLM interprets intent and maps to the consolidated tools:

61. "What's new in Azure?" (should use azure_updates_search or azure_updates_summarize)
62. "AKS news" (should use azure_updates_search with query or category filter)
63. "Azure deprecations" (should use azure_updates_search with status="Retirements")
64. "Beta features in Azure" (should use azure_updates_search with status="In preview")
65. "Is there anything about Azure Cosmos DB?" (should use azure_updates_search with query or category)
66. "Recent Azure announcements" (should use azure_updates_search)
67. "Azure update feed health check" (should use ping)
68. "Give me the big picture of Azure updates" (should use azure_updates_summarize)

---

## Verification Approach

To verify the MCP server is working correctly:

1. **Health Check**: Run prompt #1 or #2 - should return status "ok" with timestamp
2. **Data Flow**: Run prompt #5 - should return actual Azure updates with all fields populated in structured response
3. **Filtering**: Run prompt #8 - should return `filters_applied: {query: "storage", status: "In preview"}` and only matching updates
4. **Categories**: Run prompt #10 - should return category names with counts > 0
5. **Error Handling**: Run prompt #35 - should return `{total_found: 0, updates: [], filters_applied: {...}}`, not an error
6. **Summary**: Run prompt #27 - should return statistical breakdown with `by_status`, `top_categories`, and `highlights`
7. **Combined Filters**: Run prompt #42 - should show all filters in `filters_applied` field
