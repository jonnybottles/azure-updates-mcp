# Test Prompts for Azure Updates MCP Server

## Overview

This document contains test prompts to exercise all 10 tools in the Azure Updates MCP server. The prompts are organized by category: basic functionality, edge cases, and real-world scenarios.

---

## 1. Basic Tool Testing (Individual Tools)

### ping
1. "Check if the Azure Updates MCP server is running"
2. "What's the health status of the Azure updates service?"

### list_updates
3. "Show me the 5 most recent Azure updates"
4. "List the latest 20 Azure service updates"
5. "What are the newest Azure announcements?"

### search_updates
6. "Search for Azure updates related to Kubernetes"
7. "Find any Azure updates mentioning 'security'"
8. "Search for 'storage' updates that are in preview"
9. "Look for Azure updates about 'AI' or 'machine learning'"

### list_categories
10. "What categories of Azure updates are available?"
11. "Show me all the Azure service categories and how many updates each has"

### get_updates_by_category
12. "Show me all updates for Azure Kubernetes Service"
13. "Get networking-related Azure updates"
14. "What's new in Azure SQL Database?"
15. "Find Compute updates that have launched"

### get_updates_by_date_range
16. "Show me Azure updates from the last week"
17. "What Azure updates were published in January 2025?"
18. "Get all updates between 2025-01-01 and 2025-01-15"
19. "Show me retirements announced this month"

### get_update_details
20. "Get the full details for this specific Azure update: [use a GUID from list_updates]"

### get_previews
21. "What Azure features are currently in preview?"
22. "Show me preview features for Azure Kubernetes Service"
23. "List all preview announcements, limit to 30"

### get_retirements
24. "What Azure services are being retired?"
25. "Show me any retirement notices for storage services"
26. "Are there any upcoming Azure retirements I should know about?"

### get_updates_summary
27. "Give me an overview of recent Azure updates"
28. "What's the summary of Azure update activity?"
29. "Show me a dashboard of Azure updates"

---

## 2. Edge Cases and Error Handling

### Limit Parameter Testing
30. "Show me exactly 1 Azure update"
31. "List 100 Azure updates" (max limit)
32. "Show me 150 Azure updates" (exceeds max - should clamp to 100)

### Empty/No Results
33. "Search for Azure updates about 'xyznonexistent123'"
34. "Get updates for category 'FakeServiceThatDoesNotExist'"
35. "Show me Azure updates from 1990-01-01 to 1990-12-31" (no results expected)

### Invalid Input
36. "Get update details for GUID 'invalid-guid-12345'" (should return null/not found)
37. "Search for updates with status 'InvalidStatus'"

### Date Range Edge Cases
38. "Show me Azure updates from 2025-12-31 to 2025-01-01" (end before start)
39. "Get updates from today only" (single day range)

---

## 3. Real-World Scenarios

### Planning and Migration
40. "I'm planning to use Azure Kubernetes Service - what recent updates and previews should I know about?"
41. "We use Azure SQL Database - are there any retirements or breaking changes coming?"
42. "What Azure services have launched new features this month?"

### Security and Compliance
43. "Find any Azure security-related updates"
44. "Search for compliance or governance updates in Azure"
45. "What security features are in preview right now?"

### Multi-Tool Workflows
46. "First show me the categories, then get the top 10 updates for the most popular category"
47. "Get a summary of updates, then show me details on any retirements mentioned"
48. "Search for 'API' updates, then get full details on the most recent one"

### Specific Service Deep-Dives
49. "I need a complete picture of Azure Functions - show me recent updates, previews, and any retirements"
50. "What's happening with Azure OpenAI Service? Any new features or changes?"
51. "Give me all updates related to 'containers' or 'Kubernetes'"

### Status-Specific Queries
52. "What features launched in Azure this week?"
53. "Show me everything currently in development for Azure"
54. "Which Azure services have upcoming retirements in the database category?"

### Comparative/Trend Analysis
55. "Compare the number of updates across different Azure categories"
56. "What's the most active Azure service area based on recent updates?"

---

## 4. Natural Language Variations

These test how well the LLM interprets intent and maps to tools:

57. "What's new in Azure?" (should use list_updates or get_updates_summary)
58. "AKS news" (should use search_updates or get_updates_by_category)
59. "Azure deprecations" (should map to get_retirements)
60. "Beta features in Azure" (should map to get_previews)
61. "Is there anything about Azure Cosmos DB?" (search or category filter)
62. "Recent Azure announcements" (list_updates)
63. "Azure update feed health check" (ping)

---

## Verification Approach

To verify the MCP server is working correctly:

1. **Health Check**: Run prompt #1 or #2 - should return status "ok" with timestamp
2. **Data Flow**: Run prompt #5 - should return actual Azure updates with all fields populated
3. **Filtering**: Run prompt #8 - should return only "In preview" status updates matching "storage"
4. **Categories**: Run prompt #10 - should return category names with counts > 0
5. **Error Handling**: Run prompt #33 - should return empty list, not an error
