# Unit 6C Owner QA Notes — Background Diversity Accepted

Owner QA after reviewing Unit 6C library and forest candidates:

```text
둘다 괜찮은거같아
```

## Interpretation

Both additional `scene_background` diversity candidates are acceptable as broad background directions.

Accepted directions:

```text
6C-A fantasy noble library/private study: acceptable
6C-B mystical rainy forest/stream woodland: acceptable
```

## Prompting process question

Owner asked:

```text
큰방향은 프롬프트 짤때는 어떤식으로 진행하고 있어?
```

Current scene_background prompting process:

```text
1. Start from asset role and intended use as a VN background.
2. Separate strict taxonomy tags from semantic/style intent.
3. Use validated tags for structural anchors: indoors/outdoors, library/forest/hallway, window/bookshelf/tree, night/rain/fog.
4. Add short semantic_prompt for what the viewer should understand the place to be.
5. Add short style_prompt for material, lighting, mood, and genre identity.
6. Keep negative wrapper for no humans/text/watermarks.
7. Generate one candidate, then owner QA decides if semantic drift requires prompt correction.
```

## Unit status

```text
Unit 6C: accepted
scene_background broad direction: acceptable with tag segment + semantic/style segment
```
