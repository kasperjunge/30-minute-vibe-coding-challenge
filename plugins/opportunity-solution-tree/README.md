# Opportunity Solution Tree Plugin

A Claude Code plugin that helps pre-PMF startups navigate product discovery using the Opportunity Solution Tree framework. Avoid building something nobody wants by systematically exploring the problem space before committing to solutions.

## What It Does

This plugin provides an AI agent skill that guides you through creating and maintaining an Opportunity Solution Tree - a living document that maps:

1. **Outcome**: What you're trying to learn or achieve (your learning goal)
2. **Opportunities**: Real problems your target customers experience
3. **Solutions**: Multiple ways you might address each opportunity
4. **Experiments**: Specific tests to validate your assumptions

The skill helps you avoid common pitfalls like jumping to solutions too quickly, confusing features with problems, or building before validating.

## When to Use This Plugin

Use this plugin when you need help with:

- Product discovery and validation for pre-PMF startups
- Identifying which problems are worth solving
- Structuring customer research findings
- Mapping opportunities before building solutions
- Designing experiments to test assumptions
- Understanding the Opportunity Solution Tree framework
- Avoiding "build it and they will come" mistakes
- Finding product-market fit systematically

## How It Works

The skill guides you through the four levels of the OST:

### 1. Outcome (The Root)
Not a polished KPI, but a learning goal or early traction signal:
- "Validate that [ICP] will pay for a solution to [problem]"
- "Get 10 companies actively using our prototype weekly"
- "Find the problem worth building a company around in [market]"

### 2. Opportunities (First Branches)
Real customer problems from conversations and research:
- Framed from the customer's perspective
- Solution-agnostic
- Have real consequences (pass the "so what?" test)
- Right level of altitude (not too generic, not too specific)

### 3. Solutions (Next Layer)
Multiple specific ideas per opportunity:
- Range from lightweight to built-out
- Include non-scalable/manual options
- Clearly connect to the opportunity
- Diverse in approach (software, services, templates, etc.)

### 4. Experiments (The Leaves)
Time-bound tests with clear hypotheses:
- "We believe [solution] will [result] for [opportunity]"
- "We'll know we're right when [measurable outcome]"
- Completable in days or weeks, not months
- Test specific assumptions before building

## Example Usage

```
You: I'm building a tool for small e-commerce brands. How do I validate what to build?

Claude: [Activates opportunity-solution-tree skill]

Let me help you use the Opportunity Solution Tree framework to explore the problem space systematically.

First, let's clarify your outcome. At the pre-PMF stage, this should be a learning goal. For example:
- "Validate that small e-commerce brands will pay for [specific problem solution]"
- "Identify which segment within small e-commerce has the most urgent need"
- "Get 10 brands actively using our prototype weekly"

What are you trying to learn or validate?

[... guided discovery process follows ...]
```

The skill automatically activates when you ask about:
- Product discovery or validation
- Opportunity Solution Trees
- What to build next (pre-PMF context)
- Customer research and problem validation
- Running experiments to test assumptions

## Common Pitfalls Avoided

The skill helps you avoid these mistakes:

- **Solution disguised as outcome**: Smuggling your solution into the outcome position
- **Feature-opportunities**: Listing features you want to build instead of customer problems
- **Tunnel vision**: Only exploring 1-2 opportunities that match your preconceived solution
- **Armchair research**: Filling the tree based on assumptions instead of customer conversations
- **Equal weighting**: Treating all opportunities as equally important
- **Too big to test**: Only considering solutions that take months to build
- **Vague experiments**: "Get feedback" instead of specific hypotheses with success criteria
- **Static tree**: Creating once and never updating

## Skills Included

### `opportunity-solution-tree`

An autonomous agent skill that provides expert guidance on creating and maintaining OSTs for pre-PMF startups. Claude will automatically invoke this skill when relevant to your query.

## Installation

This plugin is part of the 30 Minute Vibe Coding Challenge marketplace.

To install:
```
/plugin install opportunity-solution-tree@30-minute-vibe-coding-challenge
```

## About the Framework

The Opportunity Solution Tree is a continuous discovery framework that helps startups:

- **Separate learning from building**: Most early effort should be understanding opportunities, not creating solutions
- **Stay problem-focused**: The problem is usually more stable than your solution pre-PMF
- **Embrace multiple options**: You don't know which problem is most valuable yet
- **Make learning explicit**: Articulate what you're testing and what would change your mind

The tree is a living document that evolves as you learn from experiments and customer conversations. It's about being honest about what you know, what you're guessing, and what you need to learn next.

## Pre-PMF Mindset

This framework is specifically designed for pre-PMF startups because it:

- Resists the urge to build immediately
- Forces you to articulate assumptions before testing them
- Keeps multiple opportunities in play until validated
- Makes it safe to invalidate ideas early (before building)
- Creates a systematic path from uncertainty to product-market fit

## Requirements

- Claude Code v1.0.0 or higher
- This is a skill plugin, so Claude will automatically use it when relevant to your conversation

## License

MIT

## Author

Kasper Junge
