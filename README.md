# LLM Fine Tuning

## Context
chatGPT is good at solving D&A-type problems, but not the hard ones.

If we take the latest problems that come out, for example, the latest hard problem released on LeetCode as I write these lines:

<img src ="img/1.JPG" alt="Problem Statement"/>

## Attempted Solution
When asked to solve it, the answer given is wrong. Below are the images of the attempted solution:

<div style="display:flex; justify-content:space-between;">
  <img src="img/2.JPG" alt="Solution Attempt 1" style="width: 45%; margin-right: 10px;"/>
  <img src="img/3.JPG" alt="Solution Attempt 2" style="width: 45%;"/>
</div>

<br/>

## The Idea
The goal is to design a more efficient model for code questions.

## Project Goal
My aim is to create a browser extension, in which you can copy and paste a DSA (Data Structure and Algorithm) type question, and the extension will provide the answer to the question.

---

## My Work / Research

### First step

At first, I thought I'd use a model that had already been made and finetuned on huggingface to see what results could be obtained. 

Unfortunately, I ran into a problem:
**Canceled future for execute_request message before replies were done**

**The Kernel froze when executing code in the active cell or a previous cell. Please check the code in the cell(s) to identify a possible cause of the failure. Click [here](https://aka.ms/vscodeJupyterKernelCrash) for more information. For more information, see Jupyter log.**

In other words: I don't have enough memory to run the model on my computer, even taking the model with the fewest parameters and trying with colab,, the models used 7B of data and are too heavy.


### New idea

Two solutions: pay google colab pro (no thanks), or think again.

On second thought, I found a provider that, I think, hosts the models on their servers, and with the help of an API lets us interact with them and even finetune them. Advantage: Free plan $5

Disadvantage: I invite you to read version1.ipynb to understand that the results weren't convincing.

### Hand to wallet

And if the solution could be found in our dear friend openAI.

  <img src="img/4.JPG"/>

1,000 tokens is about 750 words

Using ChatGPT, I told him to create a solution for the first 5 leetcode exos and to count the average number of characters, and he came up with 365.75 characters (counting spaces, of course).
we can add the fact that there's a little sentence before talking about the datastructure used and a little sentence after, talking about time and space complexity.

Let's round up the total output to an average of 400 characters.

For the input, it varies according to the statement. If we do as above and take the first 5 leetcode exos, we get : 200 characters on average for input.


If we consider that, on average, one token = 4 characters.

We'll have :

- for input: 200 characters --> 50 tokens
- for output: 400 characters --> 100 tokens
- For training: input + output = 600 characters --> 150 tokens

According to training prices, for GPT-3.5-turbo :

For 
0.0080 = 1000 tokens
1000 raw of data = 150000 tokens

so if I want to enter 1000 examples of exercises, it will cost me: 0.0080 * 150 = 1.2$.

the cost of then testing the model with a few exercises will be lower: if I do fifteen or so tests, it will cost me less than 1000 tokens, i.e. less than $0.008.

The main cost is in training.


## Davinci-002 or GPT-3.5-turbo

> Davinci-002 tends to be better at understanding and generating responses for complex tasks. It has been trained on a wider variety of data and for longer, allowing it to develop a deeper understanding of nuanced prompts.

> GPT-3.5-turbo is designed for more rapid responses and may not perform as well on highly complex tasks.

Code-Related Tasks:

> For generating code and solving programming-related queries, Davinci-002 is typically superior. It's been shown to have a better grasp of syntax and logic required for programming, which would be beneficial for solving hard LeetCode problems.

> While GPT-3.5-turbo can handle code to some extent, it might not be as precise or efficient as Davinci-002 when dealing with more complex or less common problems.


I will go for Davinci-002.

We can see on the OpenAPI doc : "You can also fine-tune a fine-tuned model which is useful if you acquire additional data and don't want to repeat the previous training steps."
I'm gonna fine-tune my model two time, firstly on a small dataset, to see if my expectation of the cost is correct.


## Advice to get better result 

> I should test my prompt maybe directly on chatGPT, and see which one is the best for solving DSA question.I will when use the prompt for both asking questions and fine tuning the model.


## Let's code

For  davinci-002, you can follow the prompt completion pair format used for legacy fine-tuning as shown below :

```json
{"prompt": "<prompt text>", "completion": "<ideal generated text>"}
{"prompt": "<prompt text>", "completion": "<ideal generated text>"}
{"prompt": "<prompt text>", "completion": "<ideal generated text>"}
```


First Step for us :
setup our data.

the prompt needs to contains the exercise and an instruction, like "Write a Python function with good time complexity that solves this problem."


the completion needs to contain the code with format answer ! Using space and \n to respect the indentation. Unfortunately the datasets that can be found on huggingface doesn't contain the formatting that i want https://huggingface.co/datasets?search=leetcode

C'est parti pour récupérer les données. Comme je me suis dit que le modèle savait déjà résoudre casiment tous les easy mais moins les medium et surtout les hard, je vais sélectionner des exos récents dans la catégorie medium et hard.

Etape à suivre selon moi :
1. Créer un autre compte leetcode (en espérant ne pas me faire ban IP et perdre ma streak leetcode 🙏)
2. émuler avec Puppeteer le site leetcode, allé sur le bon exercice (liste d'id d'exercices que j'aurai prédéfini à la main)
3. Allez dans l'onglet solution, cliqué sur python, et prendre la première solution
4. Allez dans l'endroit du code et le récupérer

Allons tester tout ça.


UPDATE : enfait j'ai trouvé en cherchant sur des forums et post stackoverflow, un lien github d'une personne qui répertorie les schéma graphQL de leetcode ! Pas évident pour le souligner, car Leetcode disabled its introspection feature which will let everybody know all the schem (because It's not safe for a company to expose its graphql schema in production)

j'ai testé plusieurs requêtes notamment :
curl 'https://leetcode.com/graphql'   -H 'Content-Type: application/json' --header 'Referer: https://leetcode.com' --header 'Cookie: LEETCODE_SESSION=your_leetcode_session; csrftoken=your_csrf_token' \  --data-raw '{"query":"query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) { questionSolutions( filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags} ) { hasDirectResults totalNum solutions { id title commentCount topLevelCommentCount viewCount pinned isFavorite solutionTags { name slug } post { id status voteCount creationDate isHidden author { username isActive nameColor activeBadge { displayName icon } profile { userAvatar reputation } } searchMeta { content contentType commentAuthor { username } replyAuthor { username } highlights } } } }","variables":{"questionSlug":"two-sum","skip":0,"first":1,"orderBy":"hot","languageTags":["python3"],"topicTags":[]}}'

où vous devez remplacé your_leetcode_session et your_csrf_token par les valeurs que vous trouvez dans les cookies lorsque vous lancez une session leetcode. Malheuresement je n'arrive pas à obtenir un bon résultat, je suis bloqué avec :

``` html
<div id="summary">
  <h1>Forbidden <span>(403)</span></h1>
  <p>CSRF verification failed. Request aborted.</p>
```

Then to upload the data :
https://platform.openai.com/docs/api-reference/files/create

curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@mydata.jsonl"

Then start the finetune :
https://platform.openai.com/docs/api-reference/fine-tuning


curl https://api.openai.com/v1/fine_tuning/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "training_file": "MY FILE ID FROM PREVIOUS REQUEST",
    "model": "davinci-002"
  }'



tool to automatically test the solutions 
https://github.com/skygragon/leetcode-cli?tab=readme-ov-file
