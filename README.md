# HTqq html query extractor

Use xpath and css selectors on command line.
Uses lxml and cssselect libraries.

HTqq reads whole html document from stdin or interprets stdin as one html
document per line if given **-l** option. The rest of the arguments specify a
pipeline of xpath or css extractors - that is each argument is a separate
pipeline step.

Eg. **htqq a @href** creates a pipeline with two steps. The first one (a)
extracts all links and the second extracts href attribute from them.

Example usage
```
# 1. Extract all paragraphs (p)
$ echo '<html><body><p>Hello</p><p>World</p></body></html>' | htqq p
<p>Hello</p>
<p>World</p>

# 2. Extract text from them
$ echo '<html><body><p>Hello</p><p>World</p></body></html>' | htqq p 'text()'
Hello
World

# 3. Extract all links (a) and then all href attributes (@href)
$ echo '
<a href="http://example1.com"></a>
<a href="http://example2.com"></a>
<a href="http://example3.com"></a>' | htqq a @href
http://example1.com
http://example2.com
http://example3.com

# 4. Read each div on its line and extract using css class selector
$ echo "<div class='A'>AAA</div>\n<div>BBB</div>" | htqq -l .A 'text()'
AAA

# 5. Use css negation
$ echo "<div class='A'>AAA</div>\n<div>BBB</div>" | htqq -l ':not(.A)' 'text()'
BBB
```
