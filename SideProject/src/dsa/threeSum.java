// // Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.

// Notice that the solution set must not contain duplicate triplets.
// Input: nums = [-1,0,1,2,-1,-4]
// Output: [[-1,-1,2],[-1,0,1]]

package dsa;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class threeSum {
    public List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> res = new ArrayList<>();

        for (int i = 0; i < nums.length - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) continue; // skip duplicate fixed value

            int l = i + 1;
            int r = nums.length - 1;

            while (l < r) {
                int sum = nums[i] + nums[l] + nums[r];
                if (sum == 0) {
                    res.add(Arrays.asList(nums[i], nums[l], nums[r]));
                    l++;
                    r--;
                    while (l < r && nums[l] == nums[l - 1]) l++; // skip duplicates
                    while (l < r && nums[r] == nums[r + 1]) r--; // skip duplicates
                } else if (sum < 0) {
                    l++;
                } else {
                    r--;
                }
            }
        }
        return res;
    }

    public List<List<Integer>> threeSumPractice(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        Arrays.sort(nums);

        for(int i = 0;i<nums.length-2;i++){
            if(i>0 && nums[i] == nums[i-1]) continue;

            int j = i+1;
            int k = nums.length - 1;

            while(j<k) {
                int sum = nums[i]+nums[j]+nums[k];
                if (sum == 0) {
                    res.add(new ArrayList<>(List.of(nums[i], nums[j], nums[k])));
                    j++;
                    k--;
                    while (j<k &&  nums[j] == nums[j-1]) j++;
                    while (j<k && nums[j] == nums[k+1]) k--;
                }
                else if (sum < 0) j++;
                else k--;
            }

        }
        return res;
    }
}
