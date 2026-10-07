# gitignore-match

按 gitignore 规则判断路径是否被忽略：规则顺序、取消规则、目录规则、锚定与通配符。只用 Python 标准库。

```
python3 -m unittest discover -s tests
python3 -m ignorematch --sample=negate
python3 -m ignorematch --sample=star
python3 -m ignorematch --sample=anchor
python3 -m ignorematch --sample=dironly
python3 -m ignorematch --sample=work
```

## 口径

- **顺序**：规则按出现顺序生效，最后一条命中的规则决定结果。
- **取消**：`!` 开头的规则表示不忽略。
- **目录**：以 `/` 结尾的规则只对目录生效；被忽略目录下的所有路径都算被忽略。
- **锚定**：以 `/` 开头的规则只从根匹配；含 `/` 的规则按整条路径匹配；不含 `/` 的规则匹配任意层级的同名条目。
- **通配**：`*` 不跨 `/`，`**` 跨目录。
- **查找**：按路径首段建索引，命中的候选规则不再全表扫。

## 不变量

- 最后一条命中的规则决定结果。
- 被忽略目录下的路径一定被忽略。
- `scanned` 不随规则数乘查询次数放大：八百条规则查八百次的 `scanned` 不超过 6000。

## 输出契约

`is_ignored(patterns, path, isdir)` 返回布尔；`filter(patterns, paths)` 返回被忽略的路径。
场景打印一行 JSON。`--sample=work` 打印 `{"rules": N, "scanned": N}`。
