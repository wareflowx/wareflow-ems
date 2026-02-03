# Instructions for Claude

## Language
- Always speak and write in English throughout this conversation

## Feature Completion & Release Process
When a feature is completed:
1. Use `gh` CLI to fetch the latest tag: `gh release list --limit 1`
2. Create a new tag for the new feature release
3. Publish the exe with the new tag

## Issue Creation Process
When adding a new issue:
1. First create an MD file in `docs/issues/` directory
2. Write the issue in English, without metadata
3. Then create the issue using `gh` CLI: `gh issue create --title "Title" --body "Body content"`
4. Verify that labels are coherent and existent before applying them
