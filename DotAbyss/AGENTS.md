# Game Play Agent

## Obtain window
1. Firstly run `utils.find_app_window()` to detect whether game is up
2. Next run `graphics.take_snapshot()` to grab game window context

## Controls
1. All available in `Input` moudule, such as `Input.click(x, y)`

## Skill: gift character
Use this sequence to give gifts to the currently selected character.

1. Run with admin access when the game is elevated.
2. Run `utils.find_app_window()` and `graphics.take_snapshot()` before clicking.
3. On the character detail page, check whether the `絆` level is `0`. If it is not `0`, press the next-character arrow from step 11 and repeat this check on the next character.
4. Click `交流` on the left side to open the exchange page, then click the gift button labeled `贈る` in the lower-right exchange panel.
5. In the gift panel, check that the basic giftbox stock is at least `14`. If there are fewer than `14`, abort gifting.
   - Basic giftbox is the first gift row.
6. Click the basic giftbox row's `+` button exactly `14` times, then click the large `贈る` button at the bottom of the gift panel.
7. If a confirmation dialog opens, verify the shown gift count, then click the yellow `贈る` button.
8. After gifting, dismiss story unlock prompts by clicking `スキップ` unless the user asks to view them.
9. If a staff-registration prompt appears, click `キャンセル` unless the user asks to register the character. If the game enters the staff scene anyway, click the top-left back icon to return.
10. If an ability-unlock dialog appears, click `キャラ詳細へ`. Otherwise, to return to character info, close the gift panel, then click the top-left back icon. Do not click the left `キャラ詳細` icon for this return path because it can hide the next-character arrow.
11. On the character info page, the next-character arrow is the large glowing right chevron beside the character, around app-relative `(619, 412)`. Verify the character name changes after pressing it.

### Fast path notes

- Avoid repeated manual snapshots. Capture only at checkpoints: initial character detail, gift panel stock, confirmation dialog count, and final character detail.
- Wait for loading to finish after clicking `交流` before clicking `贈る`; clicking the gift tile during loading wastes a cycle.
- Use app-relative coordinates for the known controls:
  - `交流`: around `(68, 174)`
  - gift tile `贈る`: around `(1188, 642)`
  - basic giftbox `+`: around `(1200, 141)`
  - gift panel bottom `贈る`: around `(1080, 654)`
  - confirmation dialog yellow `贈る`: around `(756, 565)`
  - story `スキップ`: around `(546, 490)`
  - top-left back: around `(48, 36)`
- Batch the fourteen `+` clicks in one command with a short delay between clicks, then capture once to verify the confirmation shows `14`.
