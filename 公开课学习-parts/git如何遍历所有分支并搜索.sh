#!/bin/bash
for branch in $(git branch -a | sed 's/remotes\/origin\///'); do
    echo "Searching in branch: $branch"
    git checkout $branch --quiet || continue  # 切换到分支，如果分支不存在则跳过
    git grep -n "ego_feature_tensor" -- ':(top)' || true  # 在当前分支中搜索字符串
    git checkout - --quiet  # 切换回主分支或其他分支（根据你的需求）
done

