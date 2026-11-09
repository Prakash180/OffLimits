package dsa;

public class MaxProfit {
    public int maxProfit(int[] prices) {
        int minBuy = Integer.MAX_VALUE;
        int profit=0;

        for (int p : prices){
            if(p < minBuy)
                minBuy = p;
            else{
                profit = Math.max(profit, p-minBuy);
            }
        }
        return profit;
    }
}
