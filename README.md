# Screen_Region_Selector
提供一個螢幕區域範圍的選擇視窗，選取完畢後回傳選取區域的 (Top, Left, Widthm Height) 四項資料

# 使用範例
### 1 程式執行後，出現白色為透明的視窗顯示在最上層時，表示開始選取視窗範圍

![image](https://github.com/JasonHongOO/Screen_Region_Selector/blob/main/Images/1%20(1).jpg)

### 2 使用滑鼠按住後拖拉，取選出目標範圍

![image](https://github.com/JasonHongOO/Screen_Region_Selector/blob/main/Images/1%20(2).jpg)

### 3 選取完區域範圍後，提供一個方框視窗
讓使用者再次微調選取範圍，在方框中將滑鼠按住則可拖拉整個方框的位置，這邊還額外提供兩個功能:
- "儲存" 當前區域中的畫面到指定資料夾
- "複製" 當前區域中的畫面到 "剪貼簿" (在小畫家按 ctrl+v 就會貼上畫面)

![image](https://github.com/JasonHongOO/Screen_Region_Selector/blob/main/Images/1%20(3).jpg)

調整視窗後的示意圖

![image](https://github.com/JasonHongOO/Screen_Region_Selector/blob/main/Images/1%20(4).jpg)

### 4 最後按下 Close 按鈕按關閉視窗就回回傳 (Top, Left, Widthm Height)，並同時將資料儲存在 Coordination.json 