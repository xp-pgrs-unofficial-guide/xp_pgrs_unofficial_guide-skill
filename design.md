目前我们已经有了西浦博士生非官方手册 https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide 仓库，以 submodule 的形式存放在 ./xp_pgrs_unofficial_guide。它之前是以 latex 格式编写的，以方便生成 pdf。但随着 agents 的崛起，每个人都开始有配置自己的个人助理，这让我觉得可以以更方便的形式来组织这个手册，让 agents 更容易理解和使用，从而让每个人都可以跟方便的来获取、使用这个手册。

但我不打算重写这个手册，因为工作量实在是太大了，而且 latex 格式也确实方便生成 pdf，方便打印和阅读。所以，我的想法是，在不破坏原有的 latex 格式的基础上，让 agents 更容易理解和使用这个手册。

为此，我设想制作一个 skill，让无论是谁的 agent 都可以通过这个 skill 来获取、使用这个手册。

考虑到已有的 latex 项目是使用 \input 语句来组织各个章节的，我们需要在 skill 中提到这个事情，并指引 agent 以一种系统性的方法来理解这个手册。例如，agent 可以先阅读 main.tex，了解这个手册的整体结构，然后再阅读各个章节，了解各个章节的具体内容存放在哪里。

另外，latex 项目中使用了大量的图片，这意味着，为了完整的理解手册的内容，agent 需要能够查看图片。因此，我们需要在 skill 中提到这个事情，并引导 agent 检查自己是否能够理解图片，如果不能，则引导 agent 向用户反馈这个问题。

考虑到 latex 项目是以 submodule 的形式引入到此项目中的，应该在 skill 中提到这个事情，并引导 agent 检查 submodule 是否存在，如果不存在，则需要 agent 首先执行 git submodule update --init --recursive 命令来更新 submodule。