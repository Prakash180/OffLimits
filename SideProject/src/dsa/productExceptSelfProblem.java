package dsa;

// Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].

// The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.

// You must write an algorithm that runs in O(n) time and without using the division operation.

 

// Example 1:

// Input: nums = [1,2,3,4]
// Output: [24,12,8,6]
// Example 2:

// Input: nums = [-1,1,0,-3,3]
// Output: [0,0,9,0,0]

class productExceptSelfProblem {
    public int[] productExceptSelf(int[] nums) {
        int productLRArr[] = new int[nums.length];
        productLRArr[0] = nums[0];
        
        int productRLArr[] = new int[nums.length];
        productRLArr[nums.length-1]=nums[nums.length-1];
        
        int resArr[] = new int[nums.length];
        
        for (int i=1;i<nums.length;i++){
            productLRArr[i] = nums[i]*productLRArr[i-1];
        }
        for (int j=nums.length-2;j>=0;j--){
            productRLArr[j] = nums[j]*productRLArr[j+1];
        }

        for(int i=0;i<nums.length;i++){
            if(i==0)
                resArr[i] = productRLArr[i+1];
            else if(i==nums.length-1)
                resArr[i] = productLRArr[i-1];
            else
                resArr[i] = productLRArr[i-1] * productRLArr[i+1];
        }
        return resArr;

    }

    public int[] productExceptSelfOptimized(int[] nums) {
        int[] resArr = new int[nums.length];

        resArr[0] = 1;
        for (int i = 1; i < nums.length; i++) {
            resArr[i] = resArr[i - 1] * nums[i - 1];
        }

        int suffixProduct = 1;
        for (int i = nums.length - 1; i >= 0; i--) {
            resArr[i] = resArr[i] * suffixProduct;
            suffixProduct *= nums[i];
        }

        return resArr;
    }
}