# Contributing to Text2Video

## Contribute with Pull Requests

1. Fork the repo and create your branch from `master`.
2. Issue that pull request!

## Feature Suggestion

Request features using Github issues.

- Use a clear and descriptive title for the issue to describe the suggestion
- Explain why this enhancement would be useful to users

## :bug: Bug Reports

To report a bug create a Github issue.

- Use a clear and descriptive title to describe the issue
- Describe the exact steps to reproduce the problem
- Provide what happened after you followed the steps and what was wrong with that behavior
- Explain what behavior you were expecting to see and why

## Production

Text2Video is deployed on DigitalOcean

- Create a `.env.production` file in the root directory containing this:

```
WEBSITE_PORT=80
```

Run `docker-compose --env-file .env.production up -d`
