package dsa;

//<!-- 152. Maximum Product Subarray
//Given an integer array nums, find a subarray that has the largest product, and return the product.
//
//The test cases are generated so that the answer will fit in a 32-bit integer.
//
//Note that the product of an array with a single element is the value of that element.
//
//nums = [2,3,-2,4]
//-->

class maxProductSubArray {
    public int maxProduct(int[] nums) {
        // Track both max and min products ending at current position.
        int minEndHere = nums[0];
        int maxEndHere = nums[0];
        int res = nums[0];

        for(int i=1; i < nums.length ; i++){
            int newMin = Math.min(nums[i], Math.min(minEndHere*nums[i], maxEndHere*nums[i]));
            int newMax = Math.max(nums[i], Math.max(minEndHere*nums[i], maxEndHere*nums[i]));

            minEndHere = newMin;
            maxEndHere = newMax;

            res = Math.max(res, maxEndHere);
        }
        return res;
    }
}