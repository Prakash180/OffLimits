package dsa;

public class MaxAvgSubarray {
    public double findMaxAverage(int[] nums, int k) {
        int l = 0;
        int r = k-1;
        int currSum = 0;
        for(int i = l;i<=r;i++)
            currSum = currSum + nums[i];
        double avg = 1. *currSum/k;
        l++;r++; 
        while(r<nums.length){
            currSum = currSum - nums[l-1] + nums[r];
            System.out.println(currSum );
            avg = Math.max(avg, 1. * currSum/k);
            l++;r++;
        }
        return avg;
    }
}