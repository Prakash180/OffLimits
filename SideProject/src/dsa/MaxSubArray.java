package dsa;

// Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
// Output: 6
// Explanation: The subarray [4,-1,2,1] has the largest sum 6.

public class MaxSubArray {
    public int maxSubArray(int[] nums) {
        // Kadane's idea: at each step, keep the best sum ending at this index.
        // If extending the previous subarray is worse than starting from nums[i],
        // start fresh. Also track the overall best sum seen so far.
        int current = nums[0];
        int best = nums[0];

        for (int i = 1; i < nums.length; i++) {
            current = Math.max(nums[i], current + nums[i]);
            best = Math.max(best, current);
        }

        return best;
    }
}