# Unit 6B Owner QA Notes — Scene Background Semantic Correction Accepted

Owner QA after reviewing Unit 6B candidate:

```text
그렇다면 의도와 비슷하게 뽑힌거같네
```

## Final interpretation

Unit 6B is accepted as a successful semantic correction of Unit 6.

Intended image:

```text
empty noble mansion / dark romantic fantasy hallway background, not a school/hospital corridor
```

Owner accepted that the result is close to the intended direction after clarification.

## Automation rule accepted

For `scene_background`, generic validated tags alone can be too weak for semantic location identity. Automation should use:

```text
strict validated tag segment
+
short semantic_prompt/style_prompt segment
```

This is now the accepted default direction for backgrounds where architecture/material/style matters.

## Unit status

```text
Unit 6: file smoke pass, semantic fail due to school-corridor drift
Unit 6B: file smoke pass, semantic correction accepted
```

## Next QA candidate

Proceed to the next independent workflow smoke, recommended:

```text
Unit 7: scene_prop_cg single smoke
```
