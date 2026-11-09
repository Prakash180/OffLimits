package dsa;

// 11. Container With Most Water
// You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

// Find two lines that together with the x-axis form a container, such that the container contains the most water.

// Return the maximum amount of water a container can store.

// Notice that you may not slant the container.


class Container {
    public int maxArea(int[] height) {
        int currwidth = height.length;

        int maxArea = 0;
        int i=0;
        int j=height.length;

        while(i<j){
            int minStick = Math.min(height[i],height[j]);
            maxArea = Math.max(maxArea, minStick*currwidth);
            if(height[i]<height[j])
                i++;
            else
                j--;
            currwidth--;
        }
        return maxArea;
    }
}
