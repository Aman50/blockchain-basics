// Picoin ICO

// Specifies the version of solidity compiler to user. Any version below 0.4.11 and above 0.5.11 will not work.
pragma solidity ^0.4.11;

contract picoin_ico{

    // Defining total number of PiCoins available to purchase in the ICO
    uint public max_picoins = 1000000;

    // Defining conversion rate between USD and PiCoin. 1 USD = 1000 PiCoins
    uint public conversion_usd_picoin = 1000;

    // Defining the number of PiCoins purchased
    uint public picoins_purchased = 0;

    // Creating mappings for each investor's equity in Picoins and USD
    // Mapping is like a dictionary in python except we cannot iterate the mapping in solidity
    mapping(address => uint) mapping_investor_to_picoin;
    mapping(address => uint) mapping_investor_to_usd;

    // Modifier is similar to a decorator. It can be used to check for a certain condition before executing the function it is placed on.
    modifier can_purchase(uint usd_invested){
        require(usd_invested*conversion_usd_picoin + picoins_purchased <= max_picoins);
        _;
    }

    // Modifier to check if the user has the required number of PiCoins they want to sell
    modifier can_sell(address investor, uint picoins_to_sell){
        require(mapping_investor_to_picoin[investor] >= picoins_to_sell);
        _;
    }

    // Function to return the Equity of the investor in usd
    // Syntax for a function in Solidity is function name(type variable) scope returns(type){}
    function equity_in_usd(address investor) external constant
    returns (uint){
        return mapping_investor_to_usd[investor];
    }

    // Function to return the Equity of the investor in PiCoin
    // Syntax for a function in Solidity is function name(type variable) scope returns(type){}
    function equity_in_picoin(address investor) external constant
    returns (uint){
        return mapping_investor_to_picoin[investor];
    }

    // Function to allow an investor to buy PiCoins
    function buy_picoin(address investor, uint usd_invested) external
    can_purchase(usd_invested)
    {
        uint picoins_purchased_1 =  usd_invested * conversion_usd_picoin;
        mapping_investor_to_usd[investor] += usd_invested;
        mapping_investor_to_picoin[investor] += picoins_purchased_1;
        picoins_purchased += picoins_purchased_1;

    }

    // Function for selling the PiCoins
    function sell_picoin(address investor, uint picoins_to_sell) external
    can_sell(investor, picoins_to_sell)
    {
        mapping_investor_to_picoin[investor] -= picoins_to_sell;
        mapping_investor_to_usd[investor] = mapping_investor_to_picoin[investor] / conversion_usd_picoin;
        picoins_purchased -= picoins_to_sell;
    }

}