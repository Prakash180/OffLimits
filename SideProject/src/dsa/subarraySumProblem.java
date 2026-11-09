

package dsa;

// 560. Subarray Sum Equals K
// Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k.
// A subarray is a contiguous non-empty sequence of elements within an array.

import java.util.HashMap;
import java.util.Map;

public class subarraySumProblem {
    public int subarraySum(int[] nums, int k) {
        int res = 0;
        for (int i = 0; i < nums.length; i++) {
            int curSum = nums[i];
            for (int j = i + 1; j < nums.length; j++) {
                curSum = curSum + nums[j];
                if (curSum == k)
                    res++;
            }
        }
        return res;
    }

    public int subarraySumOptimized(int[] nums, int k) {
        HashMap<Integer, Integer> map = new HashMap<>();
        int sum = 0;
        int res = 0;

        map.put(0, 1);
        for (int i = 0; i < nums.length; i++) {
            sum = sum + nums[i];
            if (map.containsKey(sum - k))
                res = res + map.get(sum + k);
            map.put(sum, map.getOrDefault(sum, 0) + 1);
        }
        return res;
    }
}