package dsa;

//  424. Longest Repeating Character Replacement
//  You are given a string s and an integer k. You can choose any character of the string and change it to any other uppercase English character. You can perform this operation at most k times.

// Return the length of the longest substring containing the same letter you can get after performing the above operations.

 

// Example 1:

// Input: s = "ABAB", k = 2
// Output: 4
// Explanation: Replace the two 'A's with two 'B's or vice versa.

class characterReplacement {
    public int characterReplacementfn(String s, int k) {

        int[] arr = new int[26];
        int l = 0,r = l+1;
        int curmax = 0;
        int res = 0;

        while(l<s.length()-1 && r<s.length()){

            if(l-r+1 - curmax > k) {
                l++;
                curmax--;
            }

            res = Math.max(res,curmax);
        }
        return res;
    }
}