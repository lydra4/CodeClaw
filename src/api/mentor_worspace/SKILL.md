# AI Project Recommendation Skill

Use this skill when asked to recommend AI projects based on a user's GitHub repositories and current AI trends.

## Inputs

Primary user-profile input:
- `data/01-extracted/github_profile_context.json`

Expected profile schema:
- `username`
- `total_analyzed_repos`
- `repositories[]`
  - `name`
  - `description`
  - `url`
  - `size`
  - `stargazers_count`
  - `created_at`
  - `updated_at`
  - `languages`
  - `readme_snippet`

Trend input may come from:
- web research
- a curated AI trends file
- manually provided trend notes
- future enriched data under `data/02-enriched/`

## Workflow

1. Load the GitHub profile context.
2. Infer the user's technical profile:
  - dominant languages
  - common project types
  - ML/data/AI exposure
  - engineering maturity signals
  - recent activity
  - strongest repositories
3. Use the Playwright browser tool to search the live web for this week's top trending AI frameworks, tools, and models.
4. Match trends to the user's profile:
  - strong fit: builds on existing experience
  - growth fit: requires learning one or two new areas
  - weak fit: too unrelated or too broad
5. Recommend a short list of projects.
6. Rank recommendations by:
  - profile fit
  - trend relevance
  - portfolio value
  - feasibility
  - learning upside

## Profile Analysis Heuristics

Look for:
- Python usage as a signal for ML/backend readiness
- notebooks as a signal for data science or experimentation experience
- Docker, CI, config files, and scripts as engineering maturity signals
- README quality as a signal for portfolio readiness
- recent repositories as stronger indicators than old repositories
- project descriptions and README snippets for domain interest

Avoid overclaiming. Repository metadata is evidence, not a full code review.

## Trend Matching Heuristics

Prefer project ideas that:
- connect naturally to the user's past repositories
- can be built as an MVP in a realistic timeframe
- demonstrate a current AI pattern
- produce a visible demo or measurable results
- can be explained clearly in a README or portfolio page

Avoid project ideas that:
- require large proprietary datasets
- depend on expensive infrastructure by default
- are generic chatbot wrappers with no domain angle
- are too disconnected from the user's visible skills

## Recommended Output Format

```md
# AI Project Recommendations for {username}

## Profile Summary
A short evidence-based summary of the user's GitHub profile.

## Relevant AI Trends
A short list of trends that fit this user, with brief explanations.

## Recommended Projects

### 1. {Project Name}
- Problem:
- Why it fits:
- AI Trend:
- Suggested stack:
- MVP:
- Stretch features:
- Portfolio value:
- Difficulty:

### 2. {Project Name}
...

## Suggested Build Order
Rank the projects from best first project to most ambitious.

## Next Steps
Concrete actions that the user can take this week.
```
