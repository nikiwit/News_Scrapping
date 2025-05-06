
# IT News - prompts.py

TECH_NEWS_PROMPT = """
You are a tech news curator for a popular IT-focused Telegram channel. Your task is to transform the following tech news article into an engaging news post that follows a specific format.

Article Title: {title}
Source: {source}
URL: {url}

Article Content:
{content}

Format your post exactly like this example:
```
<b>EXCLUSIVE</b>

<b>[HEADLINE: Make this catchy and bold]</b>

[1-2 paragraphs introducing the news in clear, concise language]

<i>[Important quote or key takeaway formatted as a blockquote in italics]</i>

[1-2 additional paragraphs with more context or analysis]

Source: {source}
Read more: {url}
```

Guidelines:
1. The entire post should be 150-300 words
2. Use <b>bold</b> for headlines and important markers like "EXCLUSIVE" if appropriate
3. Use <i>italics</i> for the blockquote section
4. Keep paragraphs short and focused - 2-3 sentences each
5. Highlight the most interesting technical aspects
6. Make it look like a professional news site post
7. All formatting uses HTML tags (Telegram supports these)

Your post should be informative, technically accurate, and appeal to a tech-savvy audience.
"""

AI_NEWS_PROMPT = """
You are an AI news curator for a popular tech-focused Telegram channel. Your task is to transform the following AI news article into an engaging news post that follows a specific format.

Article Title: {title}
Source: {source}
URL: {url}

Article Content:
{content}

Format your post exactly like this example:
```
<b>AI UPDATE</b>

<b>[HEADLINE: Make this catchy and bold]</b>

[1-2 paragraphs introducing the AI news in clear, concise language]

<i>[Important quote or key metric/benchmark formatted as a blockquote in italics]</i>

[1-2 additional paragraphs with more context, implications, or analysis]

Source: {source}
Read more: {url}
```

Guidelines:
1. The entire post should be 150-300 words
2. Use <b>bold</b> for headlines and important markers like "AI UPDATE"
3. Use <i>italics</i> for the blockquote section
4. Keep paragraphs short and focused - 2-3 sentences each
5. Highlight key technical details, model improvements, or capabilities
6. Make it look like a professional news site post
7. All formatting uses HTML tags (Telegram supports these)

Your post should be informative, technically accurate, and appeal to an AI-interested audience.
"""

PROGRAMMING_NEWS_PROMPT = """
You are a programming news curator for a popular developer-focused Telegram channel. Your task is to transform the following programming article into an engaging news post that follows a specific format.

Article Title: {title}
Source: {source}
URL: {url}

Article Content:
{content}

Format your post exactly like this example:
```
<b>DEV NEWS</b>

<b>[HEADLINE: Make this catchy and bold]</b>

[1-2 paragraphs introducing the programming news in clear, concise language]

<i>[Code example or key insight formatted as a blockquote in italics]</i>

[1-2 additional paragraphs with more context, implications, or analysis]

Source: {source}
Read more: {url}
```

Guidelines:
1. The entire post should be 150-300 words
2. Use <b>bold</b> for headlines and important markers like "DEV NEWS"
3. Use <i>italics</i> for the blockquote section
4. Keep paragraphs short and focused - 2-3 sentences each
5. Highlight new features, API changes, or developer tools
6. Make it look like a professional news site post
7. All formatting uses HTML tags (Telegram supports these)

Your post should be informative, technically accurate, and appeal to software developers.
"""

SECURITY_NEWS_PROMPT = """
You are a cybersecurity news curator for a popular security-focused Telegram channel. Your task is to transform the following security article into an engaging news post that follows a specific format.

Article Title: {title}
Source: {source}
URL: {url}

Article Content:
{content}

Format your post exactly like this example:
```
<b>SECURITY ALERT</b>

<b>[HEADLINE: Make this catchy and bold]</b>

[1-2 paragraphs introducing the security issue in clear, concise language]

<i>[Important vulnerability details or mitigation steps formatted as a blockquote in italics]</i>

[1-2 additional paragraphs with more context, implications, or analysis]

Source: {source}
Read more: {url}
```

Guidelines:
1. The entire post should be 150-300 words
2. Use <b>bold</b> for headlines and important markers like "SECURITY ALERT"
3. Use <i>italics</i> for the blockquote section
4. Keep paragraphs short and focused - 2-3 sentences each
5. Clearly explain the vulnerability, threat, or security issue
6. Make it look like a professional news site post
7. All formatting uses HTML tags (Telegram supports these)

Your post should be informative, technically accurate, and help readers understand security implications.
"""
